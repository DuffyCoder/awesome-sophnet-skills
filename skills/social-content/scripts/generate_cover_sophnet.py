#!/usr/bin/env python3
"""
Platform-specific cover image generation with SophNet text-to-image API.
Maps cover types to correct sizes, then handles async task polling.
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

# Always injected into negative_prompt to block text rendering and sensitive content.
# User-supplied --negative-prompt is appended after this baseline.
DEFAULT_NEGATIVE_PROMPT = (
    "text, words, letters, numbers, alphabet, characters, writing, caption, title, "
    "subtitle, label, logo, watermark, signature, stamp, typographic, font, inscription, "
    "banner, sign, signage, handwriting, calligraphy, "
    "nsfw, nudity, nude, naked, sexual, erotic, pornographic, gore, blood, violence, "
    "bloody, corpse, dead body, weapon, gun, knife, drugs, smoking, alcohol, gambling, "
    "politically sensitive, national flag, national emblem, political leader, "
    "religious symbol, hate symbol, discrimination, racist, offensive, disturbing, "
    "child exploitation, terrorism, self-harm"
)

COVER_TYPES = {
    "wechat-header": {
        "size": "900*383",
        "label": "WeChat header (900x383)",
    },
    "wechat-square": {
        "size": "200*200",
        "label": "WeChat square preview (200x200)",
    },
    "xiaohongshu": {
        "size": "1080*1440",
        "label": "Xiaohongshu cover (1080x1440)",
    },
    "guide": {
        "size": "1080*1440",
        "label": "Guide / infographic (1080x1440)",
    },
    "style": {
        "size": "1024*1024",
        "label": "Stylized photo (1024x1024)",
    },
}


def parse_bool(value):
    if value.lower() in ("true", "1", "yes", "y"):
        return True
    if value.lower() in ("false", "0", "no", "n"):
        return False
    raise argparse.ArgumentTypeError(f"invalid boolean value: {value!r}")


def create_task(api_key, prompt, model, size, negative_prompt=None,
                n=1, watermark=False, prompt_extend=True):
    merged_negative = DEFAULT_NEGATIVE_PROMPT
    if negative_prompt:
        merged_negative = f"{DEFAULT_NEGATIVE_PROMPT}, {negative_prompt}"

    payload = {
        "model": model,
        "input": {
            "prompt": prompt,
            "negative_prompt": merged_negative,
        },
        "parameters": {
            "size": size,
            "n": n,
            "watermark": watermark,
            "prompt_extend": prompt_extend,
        },
    }

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


def _strip_oss_signature(url):
    """Remove OSS signature query params to get a publicly accessible bare URL.
    SophNet's bucket allows public read, but broken signatures cause 403."""
    if not url or "?" not in url:
        return url
    bare = url.split("?")[0]
    try:
        r = requests.head(bare, timeout=10, allow_redirects=True)
        if r.status_code == 200:
            return bare
    except requests.RequestException:
        pass
    return url


def reupload_for_signed_url(api_key, raw_url):
    """Download from raw DashScope URL (using API auth), re-upload to
    SophNet OSS for a public URL, then delete the temp file.
    Returns public URL or None on failure."""
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        resp = requests.get(raw_url, headers=headers, timeout=120, stream=True)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Warning: failed to download image: {e}", file=sys.stderr)
        return None

    ext = os.path.splitext(raw_url.split("?")[0])[-1] or ".png"
    fd, tmp_path = tempfile.mkstemp(suffix=ext, prefix="cover_reup_")
    try:
        with os.fdopen(fd, "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
    except IOError as e:
        print(f"Warning: failed to write temp file: {e}", file=sys.stderr)
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        return None

    try:
        signed_url = sophnet_tools.upload_oss(tmp_path)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    if not signed_url:
        print("Warning: upload_oss returned no signed URL", file=sys.stderr)
        return None

    return _strip_oss_signature(signed_url)


def main():
    type_names = ", ".join(f"{k} ({v['label']})" for k, v in COVER_TYPES.items())

    parser = argparse.ArgumentParser(
        description="Generate platform-specific cover images via SophNet",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"Cover types:\n  {type_names}",
    )
    parser.add_argument("--type", required=True, choices=COVER_TYPES.keys(),
                        help="Cover type (determines image size)")
    parser.add_argument("--prompt", required=True, help="Image prompt")
    parser.add_argument("--negative-prompt", default=None, help="Negative prompt")
    parser.add_argument("--model", default="Qwen-Image-Plus",
                        choices=VALID_MODELS, help="Model name (default: Qwen-Image-Plus)")
    parser.add_argument("--size", default=None,
                        help="Override size (default: auto from --type)")
    parser.add_argument("--n", type=int, default=1, help="Number of images")
    parser.add_argument("--watermark", type=parse_bool, default=False,
                        help="Add watermark (default: false)")
    parser.add_argument("--prompt-extend", type=parse_bool, default=True,
                        help="Extend prompt (default: true)")
    parser.add_argument("--poll-interval", type=int, default=2,
                        help="Seconds between polls (default: 2)")
    parser.add_argument("--max-wait", type=int, default=300,
                        help="Max seconds to wait (default: 300)")
    args = parser.parse_args()

    cover = COVER_TYPES[args.type]
    size = args.size if args.size else cover["size"]

    print(f"COVER_TYPE={args.type}")
    print(f"COVER_SIZE={size}")

    api_key = sophnet_tools.get_api_key()
    if not api_key:
        print("Error: No API key found. Set SOPH_API_KEY or configure via sophnet-key skill.",
              file=sys.stderr)
        sys.exit(1)

    task_id = create_task(
        api_key, args.prompt, args.model, size,
        negative_prompt=args.negative_prompt,
        n=args.n,
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
        signed_url = reupload_for_signed_url(api_key, raw_url)
        if signed_url:
            print(f"IMAGE_URL={signed_url}")
        else:
            print(f"Warning: failed to get signed URL, raw URL may require auth: {raw_url}",
                  file=sys.stderr)
            print(f"IMAGE_URL={raw_url}")


if __name__ == "__main__":
    main()
