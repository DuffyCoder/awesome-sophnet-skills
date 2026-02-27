#!/usr/bin/env python3
"""
SophNet text-to-image generation with async task polling.
Outputs machine-friendly TASK_ID, STATUS, and IMAGE_URL lines.
"""

import argparse
import json
import os
import sys
import tempfile
import time

import requests
import sophnet_tools

API_URL = "https://www.sophnet.com/api/open-apis/projects/easyllms/imagegenerator/task"
VALID_MODELS = ["Z-Image-Turbo", "Qwen-Image", "Qwen-Image-Plus"]


def parse_bool(value):
    if value.lower() in ("true", "1", "yes", "y"):
        return True
    if value.lower() in ("false", "0", "no", "n"):
        return False
    raise argparse.ArgumentTypeError(f"invalid boolean value: {value!r}")


def create_task(api_key, prompt, model, negative_prompt=None,
                size="1024*1024", n=1, watermark=False, prompt_extend=True):
    payload = {
        "model": model,
        "input": {"prompt": prompt},
        "parameters": {
            "size": size,
            "n": n,
            "watermark": watermark,
            "prompt_extend": prompt_extend,
        },
    }
    if negative_prompt:
        payload["input"]["negative_prompt"] = negative_prompt

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    resp = requests.post(API_URL, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    for key in ("task_id", "taskId", "taskID", "id"):
        if key in data:
            return data[key]

    if isinstance(data.get("output"), dict):
        for key in ("task_id", "taskId", "taskID", "id"):
            if key in data["output"]:
                return data["output"][key]

    print(f"Error: task_id not found in response.", file=sys.stderr)
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
    """Download from raw DashScope URL (using API auth) and re-upload
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


def main():
    parser = argparse.ArgumentParser(description="SophNet image generation")
    parser.add_argument("--prompt", required=True, help="Image prompt")
    parser.add_argument("--negative-prompt", default=None, help="Negative prompt")
    parser.add_argument("--model", default="Z-Image-Turbo",
                        choices=VALID_MODELS, help="Model name")
    parser.add_argument("--size", default="1024*1024", help="Image size")
    parser.add_argument("--n", type=int, default=1, help="Number of images")
    parser.add_argument("--watermark", type=parse_bool, default=False)
    parser.add_argument("--prompt-extend", type=parse_bool, default=True)
    parser.add_argument("--poll-interval", type=int, default=2)
    parser.add_argument("--max-wait", type=int, default=300)
    args = parser.parse_args()

    api_key = sophnet_tools.get_api_key()
    if not api_key:
        print("Error: No API key found.", file=sys.stderr)
        sys.exit(1)

    task_id = create_task(
        api_key, args.prompt, args.model,
        negative_prompt=args.negative_prompt,
        size=args.size, n=args.n,
        watermark=args.watermark,
        prompt_extend=args.prompt_extend,
    )
    print(f"TASK_ID={task_id}")

    result = poll_task(api_key, task_id, args.poll_interval, args.max_wait)
    print("STATUS=succeeded")

    raw_urls = extract_urls(result)
    if not raw_urls:
        print("Error: url not found in response.", file=sys.stderr)
        print(json.dumps(result, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    for raw_url in raw_urls:
        signed_url, local_path = reupload_for_signed_url(api_key, raw_url)
        print(f"IMAGE_URL={signed_url or raw_url}")
        if local_path:
            if signed_url:
                os.unlink(local_path)
            else:
                print(f"PREVIEW_PATH={local_path}")


if __name__ == "__main__":
    main()
