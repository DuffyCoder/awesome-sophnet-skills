#!/usr/bin/env bash
#
# Generate image and download for preview
# This wrapper script calls generate_image.sh and downloads the result
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GEN_SCRIPT="${SCRIPT_DIR}/generate_image.sh"

if [[ ! -f "$GEN_SCRIPT" ]]; then
  echo "Error: generate_image.sh not found at ${GEN_SCRIPT}" >&2
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "Error: curl not found." >&2
  exit 1
fi

for arg in "$@"; do
  if [[ "$arg" == "-h" || "$arg" == "--help" ]]; then
    bash "$GEN_SCRIPT" --help
    exit 0
  fi
done

# Run the image generation script with all arguments
if ! output="$(bash "$GEN_SCRIPT" "$@" 2>&1)"; then
  echo "$output" >&2
  exit 1
fi

# Echo the original output
echo "$output"

# Extract the image URL
image_url="$(printf '%s\n' "$output" | awk '/^IMAGE_URL=/{print substr($0,11); exit}')"

if [[ -z "$image_url" ]]; then
  echo "Error: No image URL found in output" >&2
  exit 1
fi

# Generate a simple filename from task ID
task_id="$(printf '%s\n' "$output" | awk '/^TASK_ID=/{print substr($0,9); exit}')"
if [[ -z "$task_id" ]]; then
  task_id="$(date +%s)"
fi

path_no_query="${image_url%%\?*}"
ext="${path_no_query##*.}"
case "$ext" in
  jpg|jpeg|png|gif|webp|bmp)
    ;;
  *)
    ext="png"
    ;;
esac
temp_file="$(mktemp "/tmp/generated_${task_id}_XXXXXX.${ext}")"

# Download the image
if curl -fsSL "$image_url" -o "$temp_file"; then
  echo "PREVIEW_PATH=${temp_file}"
else
  rm -f "$temp_file"
  echo "Warning: Failed to download image for preview" >&2
fi
