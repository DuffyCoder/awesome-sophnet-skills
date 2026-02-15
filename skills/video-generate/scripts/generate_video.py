#!/usr/bin/env python3
"""
Sophnet Video Generation API Client

Generate videos using Sophnet Video Generation API.
Supports text-to-video, image-to-video (first frame), and image-to-video (first + last frame).
"""

import os
import sys
import time
import argparse
import json
import urllib.request
import urllib.error
import tempfile
from pathlib import Path
from typing import Optional
import subprocess


# API Configuration
API_BASE = "https://www.sophnet.com/api/open-apis/projects/easyllms/videogenerator"
UPLOAD_URL = "https://www.sophnet.com/api/open-apis/projects/upload"
TIMEOUT = 300  # 5 minutes in seconds
POLL_INTERVAL = 5  # 5 seconds

# Default values
DEFAULT_MODEL = "Wan2.6-I2V"
DEFAULT_SIZE = "1280*720"
DEFAULT_DURATION = 5


def get_api_key() -> str:
    """Get API key from binary file."""
    # Try to read from binary file
    api_key_file = Path(__file__).parent / "api_key.bin"
    if api_key_file.exists():
        try:
            with open(api_key_file, "rb") as f:
                return f.read().decode("utf-8")
        except Exception:
            pass

    # Fallback to environment
    api_key = os.environ.get("SOPH_API_KEY")
    if api_key:
        return api_key

    raise ValueError("No API key found. API key binary file or SOPH_API_KEY environment variable required.")


def upload_oss(file_path: str, api_key: str) -> str:
    """
    Upload file to OSS and return signed URL

    Args:
        file_path: Local file path
        api_key: API key for authentication

    Returns:
        str: Uploaded signed URL
    """
    if not os.path.isfile(file_path):
        raise ValueError(f"File '{file_path}' does not exist")

    try:
        import requests

        file_name = os.path.basename(file_path)
        with open(file_path, 'rb') as f:
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            files = {
                'file': (file_name, f, 'application/octet-stream')
            }
            response = requests.post(UPLOAD_URL, headers=headers, files=files)

        if response.status_code != 200:
            raise ValueError(f"Upload failed: HTTP {response.status_code}, {response.text}")

        json_data = response.json()
        result = json_data.get("result")
        if not result or not isinstance(result, dict):
            raise ValueError("Invalid response: missing 'result' field")

        signed_url = result.get("signedUrl")
        if not signed_url:
            raise ValueError("Invalid response: missing 'signedUrl'")

        return signed_url

    except ImportError:
        raise ValueError("requests library not available. Install with: pip install requests")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Upload network error: {e}")


def is_url(path: str) -> bool:
    """Check if the input string is a URL."""
    return path.startswith(("http://", "https://"))


def process_image_input(image_input: Optional[str], api_key: str) -> Optional[str]:
    """
    Process image input - return URL if it's already a URL,
    or upload to OSS and return URL if it's a local path.

    Args:
        image_input: Image URL or local file path
        api_key: API key for authentication

    Returns:
        str: Image URL
    """
    if not image_input:
        return None

    if is_url(image_input):
        return image_input

    # Upload to OSS
    print(f"Uploading image to OSS: {image_input}")
    return upload_oss(image_input, api_key)


def create_request(
    model: str,
    prompt: Optional[str],
    negative_prompt: Optional[str],
    first_frame_url: Optional[str],
    last_frame_url: Optional[str],
    size: str,
    duration: int,
    generate_audio: bool,
    draft: bool
) -> dict:
    """Build request body for video generation."""
    # Build content array
    content = []

    # Add text content
    if prompt:
        text_content = {"type": "text", "text": prompt}
        if negative_prompt:
            text_content["negative_prompt"] = negative_prompt
        content.append(text_content)

    # Add first frame
    if first_frame_url:
        content.append({
            "type": "image_url",
            "image_url": {"url": first_frame_url},
            "role": "first_frame"
        })

    # Add last frame
    if last_frame_url:
        content.append({
            "type": "image_url",
            "image_url": {"url": last_frame_url},
            "role": "last_frame"
        })

    # Build parameters
    parameters = {
        "size": size,
        "duration": duration
    }

    if generate_audio:
        parameters["generate_audio"] = True

    if draft:
        parameters["draft"] = True

    return {
        "model": model,
        "content": content,
        "parameters": parameters
    }


def make_request(url: str, data: dict, api_key: str) -> dict:
    """Make HTTP request with authentication."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    req_data = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=req_data, headers=headers)

    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def make_get_request(url: str, api_key: str) -> dict:
    """Make GET request with authentication."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def download_video(url: str, output_path: str) -> None:
    """Download video from URL to local path."""
    subprocess.run(["curl", "-L", "-o", output_path, url], check=True)


def main():
    parser = argparse.ArgumentParser(
        description="Generate videos using Sophnet Video Generation API"
    )
    parser.add_argument("--prompt", help="Text prompt (required for text-to-video)")
    parser.add_argument("--negative-prompt", help="Negative prompt")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model name (default: {DEFAULT_MODEL})")
    parser.add_argument("--size", default=DEFAULT_SIZE, help=f"Resolution (default: {DEFAULT_SIZE})")
    parser.add_argument("--duration", type=int, default=DEFAULT_DURATION, help=f"Video duration in seconds (default: {DEFAULT_DURATION})")
    parser.add_argument("--first-frame", help="First frame image URL")
    parser.add_argument("--last-frame", help="Last frame image URL")
    parser.add_argument("--generate-audio", action="store_true", help="Generate audio (Seedance-1.5-Pro only)")
    parser.add_argument("--draft", action="store_true", help="Enable draft mode (Seedance-1.5-Pro only)")
    parser.add_argument("--api-key", help="Override API key")
    parser.add_argument("--output-file", help="Save downloaded video to this path")
    parser.add_argument("--upload-oss", action="store_true", help="Upload generated video to OSS")

    args = parser.parse_args()

    # Validate arguments
    if not args.prompt and not args.first_frame:
        print("Error: Either --prompt or --first-frame is required", file=sys.stderr)
        sys.exit(1)

    # Get API key
    api_key = args.api_key or get_api_key()

    # Process image inputs - convert local paths to URLs via OSS upload
    first_frame_url = None
    last_frame_url = None

    if args.first_frame:
        first_frame_url = process_image_input(args.first_frame, api_key)
        if first_frame_url != args.first_frame:
            print(f"First Frame (OSS URL): {first_frame_url}")

    if args.last_frame:
        last_frame_url = process_image_input(args.last_frame, api_key)
        if last_frame_url != args.last_frame:
            print(f"Last Frame (OSS URL): {last_frame_url}")

    # Build request
    request_body = create_request(
        model=args.model,
        prompt=args.prompt,
        negative_prompt=args.negative_prompt,
        first_frame_url=first_frame_url,
        last_frame_url=last_frame_url,
        size=args.size,
        duration=args.duration,
        generate_audio=args.generate_audio,
        draft=args.draft
    )

    # Print request info
    print("Creating video generation task...")
    print(f"Model: {args.model}")
    print(f"Resolution: {args.size}")
    duration_str = f"{args.duration}s" if args.duration > 0 else "auto (-1)"
    print(f"Duration: {duration_str}")
    if args.prompt:
        print(f"Prompt: {args.prompt}")
    if args.negative_prompt:
        print(f"Negative Prompt: {args.negative_prompt}")
    if first_frame_url:
        print(f"First Frame: {first_frame_url}")
    if last_frame_url:
        print(f"Last Frame: {last_frame_url}")
    if args.generate_audio:
        print(f"Generate Audio: true")
    if args.draft:
        print(f"Draft Mode: true")
    print()

    # Create task
    try:
        response = make_request(f"{API_BASE}/generate", request_body, api_key)
    except urllib.error.URLError as e:
        print(f"Error: Failed to create task: {e}", file=sys.stderr)
        sys.exit(1)

    # Handle both response formats: {code: 0, data: {task_id}} or {status: 0, result: {task_id}}
    if response.get("code") != 0 and response.get("status") != 0:
        print("Error: Failed to create task", file=sys.stderr)
        print(json.dumps(response, indent=2), file=sys.stderr)
        sys.exit(1)

    task_id = response.get("data", {}).get("task_id") or response.get("result", {}).get("task_id")
    if not task_id:
        print("Error: No task ID found in response", file=sys.stderr)
        print(json.dumps(response, indent=2), file=sys.stderr)
        sys.exit(1)

    print(f"Task ID: {task_id}")
    print()

    # Poll for completion
    print("Waiting for video generation...")
    start_time = time.time()

    while True:
        current_time = time.time()
        elapsed = int(current_time - start_time)

        if elapsed >= TIMEOUT:
            print(f"Error: Timeout after {TIMEOUT}s", file=sys.stderr)
            sys.exit(1)

        try:
            status_response = make_get_request(f"{API_BASE}/generate/{task_id}", api_key)
        except urllib.error.URLError as e:
            print(f"Error: Failed to query status: {e}", file=sys.stderr)
            sys.exit(1)

        status = status_response.get("data", {}).get("status", "")
        print(f"Status: {status} ({elapsed}s)")

        if status == "succeeded":
            print("Video generation completed!")
            break
        elif status in ("failed", "cancelled"):
            print(f"Error: Video generation {status}", file=sys.stderr)
            print(json.dumps(status_response, indent=2), file=sys.stderr)
            sys.exit(1)

        time.sleep(POLL_INTERVAL)

    # Extract video URL
    video_url = status_response.get("data", {}).get("content", {}).get("video_url")
    if not video_url:
        print("Error: No video URL found", file=sys.stderr)
        sys.exit(1)

    # Extract usage info
    usage = status_response.get("data", {}).get("usage", {})
    resolution = usage.get("resolution", args.size)
    video_duration = usage.get("duration", args.duration)
    fps = usage.get("fps", "N/A")

    # Determine output path
    local_path = args.output_file
    oss_url = None

    # Download if needed
    if args.output_file or args.upload_oss:
        if not local_path:
            # Create temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                local_path = tmp.name

        print()
        print("Downloading video...")
        download_video(video_url, local_path)
        print(f"VIDEO_PATH={local_path}")

        # Upload to OSS if requested
        if args.upload_oss:
            print()
            print("Uploading to OSS...")
            try:
                oss_url = upload_oss(local_path, api_key)
                print(f"OSS_URL={oss_url}")
            except Exception as e:
                print(f"Warning: Upload to OSS failed: {e}", file=sys.stderr)
                oss_url = None

    # Print results
    print()
    print("=" * 50)
    print("Video Generation Complete!")
    print("=" * 50)
    print(f"TASK_ID={task_id}")
    print(f"STATUS=succeeded")
    print(f"VIDEO_URL={video_url}")
    if oss_url:
        print(f"OSS_URL={oss_url}")
    if local_path:
        print(f"LOCAL_PATH={local_path}")
    print()
    print("Generation Parameters:")
    print(f"  Model: {args.model}")
    print(f"  Resolution: {resolution}")
    print(f"  Duration: {video_duration}s")
    print(f"  FPS: {fps}")
    if args.prompt:
        print(f"  Prompt: {args.prompt}")

    # Use OSS URL as final link if available
    final_url = oss_url if oss_url else video_url
    print()
    print(f"Video Link: {final_url}")


if __name__ == "__main__":
    main()