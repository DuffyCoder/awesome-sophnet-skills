#!/usr/bin/env python3
"""
SophNet image editing (image-to-image) with async task polling.
Supports multiple source images via --image, --images (CSV), or --images-file.
Outputs machine-friendly INPUT_IMAGE_COUNT, TASK_ID, STATUS, and IMAGE_URL lines.
"""

import argparse
import base64
import json
import mimetypes
import os
import sys
import tempfile
import time

import requests
import sophnet_tools

API_URL = "https://www.sophnet.com/api/open-apis/projects/easyllms/imagegenerator/task"
VALID_MODELS = ["Qwen-Image-Edit-2509"]

MIME_MAP = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".png": "image/png", ".webp": "image/webp",
    ".gif": "image/gif", ".bmp": "image/bmp",
    ".avif": "image/avif",
}


def parse_bool(value):
    if value.lower() in ("true", "1", "yes", "y"):
        return True
    if value.lower() in ("false", "0", "no", "n"):
        return False
    raise argparse.ArgumentTypeError(f"invalid boolean value: {value!r}")


def is_remote_ref(ref):
    return ref.startswith(("http://", "https://", "data:image/"))


def path_to_data_uri(path):
    ext = os.path.splitext(path)[1].lower()
    mime = MIME_MAP.get(ext)
    if not mime:
        mime, _ = mimetypes.guess_type(path)
        if not mime:
            mime = "application/octet-stream"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def resolve_image(raw):
    ref = raw.lstrip("@")
    if is_remote_ref(ref):
        return ref
    if os.path.isfile(ref):
        return path_to_data_uri(ref)
    print(f"Error: --image input not found: {raw}", file=sys.stderr)
    print("Hint: for uploaded files, use the resolved path from Media Understanding logs, "
          "usually under media/inbound/images/.", file=sys.stderr)
    sys.exit(1)


def load_images_csv(csv_str):
    items = []
    for item in csv_str.split(","):
        item = item.strip()
        if item:
            items.append(item)
    return items


def load_images_file(path):
    if not os.path.isfile(path):
        print(f"Error: --images-file not found: {path}", file=sys.stderr)
        sys.exit(1)
    items = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip().rstrip("\r")
            if not line or line.startswith("#"):
                continue
            items.append(line)
    return items


def create_task(api_key, prompt, model, image_refs,
                size="1024*1024", n=1, watermark=False):
    resolved = [resolve_image(ref) for ref in image_refs]
    payload = {
        "model": model,
        "input": {"prompt": prompt, "images": resolved},
        "parameters": {
            "size": size,
            "n": n,
            "watermark": watermark,
        },
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    resp = requests.post(API_URL, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    for key in ("task_id", "taskId", "taskID", "id"):
        if key in data:
            return data[key]
        if isinstance(data.get("output"), dict) and key in data["output"]:
            return data["output"][key]

    print("Error: task_id not found in response.", file=sys.stderr)
    print(json.dumps(data, ensure_ascii=False), file=sys.stderr)
    sys.exit(1)


def poll_task(api_key, task_id, poll_interval=2, max_wait=300):
    headers = {"Authorization": f"Bearer {api_key}"}
    start = time.time()

    while True:
        elapsed = time.time() - start
        if elapsed > max_wait:
            print(f"Error: timed out after {max_wait}s.", file=sys.stderr)
            sys.exit(1)

        resp = requests.get(f"{API_URL}/{task_id}", headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        status = None
        for key in ("status", "taskStatus", "task_status"):
            if key in data:
                status = data[key]
                break
            if isinstance(data.get("output"), dict) and key in data["output"]:
                status = data["output"][key]
                break

        if status and status.lower() in ("succeeded", "success"):
            return data
        if status and status.lower() in ("failed", "error"):
            print("STATUS=failed", file=sys.stderr)
            print(json.dumps(data, ensure_ascii=False), file=sys.stderr)
            sys.exit(1)

        time.sleep(poll_interval)


def extract_urls(data):
    urls = []

    def _walk(obj):
        if isinstance(obj, dict):
            if "url" in obj and isinstance(obj["url"], str):
                urls.append(obj["url"])
            for v in obj.values():
                _walk(v)
        elif isinstance(obj, list):
            for item in obj:
                _walk(item)

    _walk(data)
    return urls


def reupload_for_signed_url(api_key, raw_url):
    """Download from raw API URL (using API auth) and re-upload
    to SophNet OSS to obtain a publicly accessible signed URL.
    Returns (signed_url, local_path) or (None, None) on failure."""
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        resp = requests.get(raw_url, headers=headers, timeout=120, stream=True)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Warning: failed to download image: {e}", file=sys.stderr)
        return None, None

    ext = os.path.splitext(raw_url.split("?")[0])[-1] or ".png"
    fd, tmp_path = tempfile.mkstemp(suffix=ext, prefix="img_reup_")
    try:
        with os.fdopen(fd, "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
    except IOError as e:
        print(f"Warning: failed to write temp file: {e}", file=sys.stderr)
        os.unlink(tmp_path)
        return None, None

    signed_url = sophnet_tools.upload_oss(tmp_path)
    if not signed_url:
        print("Warning: upload_oss returned no signed URL, keeping local file", file=sys.stderr)
        return None, tmp_path

    return signed_url, tmp_path


class AppendImageAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest, None) or []
        items.append(values)
        setattr(namespace, self.dest, items)


def main():
    parser = argparse.ArgumentParser(description="SophNet image editing")
    parser.add_argument("--prompt", required=True, help="Edit instruction prompt")
    parser.add_argument("--image", dest="images", action=AppendImageAction, default=[],
                        help="Source image (URL, data URI, or local path). Repeatable.")
    parser.add_argument("--images", dest="images_csv", default=None,
                        help="Comma-separated image refs")
    parser.add_argument("--images-file", default=None,
                        help="Read image refs from file, one per line")
    parser.add_argument("--model", default="Qwen-Image-Edit-2509",
                        choices=VALID_MODELS, help="Model name")
    parser.add_argument("--size", default="1024*1024", help="Image size")
    parser.add_argument("--n", type=int, default=1, help="Number of outputs")
    parser.add_argument("--watermark", type=parse_bool, default=False)
    parser.add_argument("--poll-interval", type=int, default=2)
    parser.add_argument("--max-wait", type=int, default=300)
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate and print input count only")
    args = parser.parse_args()

    all_images = list(args.images)
    if args.images_csv:
        all_images.extend(load_images_csv(args.images_csv))
    if args.images_file:
        all_images.extend(load_images_file(args.images_file))

    if not all_images:
        print("Error: at least one --image is required.", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print(f"INPUT_IMAGE_COUNT={len(all_images)}")
        print("STATUS=dry_run")
        return

    api_key = sophnet_tools.get_api_key()
    if not api_key:
        print("Error: No API key found.", file=sys.stderr)
        sys.exit(1)

    task_id = create_task(
        api_key, args.prompt, args.model, all_images,
        size=args.size, n=args.n, watermark=args.watermark,
    )
    print(f"INPUT_IMAGE_COUNT={len(all_images)}")
    print(f"TASK_ID={task_id}")

    result = poll_task(api_key, task_id, args.poll_interval, args.max_wait)

    print("STATUS=succeeded")

    raw_urls = extract_urls(result)
    if not raw_urls:
        print("Error: url not found in response.", file=sys.stderr)
        print(json.dumps(result, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    print(f"OUTPUT_COUNT={len(raw_urls)}")
    for i, raw_url in enumerate(raw_urls, 1):
        signed_url, local_path = reupload_for_signed_url(api_key, raw_url)
        print(f"IMAGE_URL={signed_url or raw_url}")
        if local_path:
            if signed_url:
                os.unlink(local_path)
            else:
                print(f"PREVIEW_PATH={local_path}")


if __name__ == "__main__":
    main()
