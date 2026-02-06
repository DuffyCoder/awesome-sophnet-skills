#!/usr/bin/env bash
#
# Generate image and download for preview
# This wrapper script calls generate_image.sh and downloads the result
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the image generation script with all arguments
if ! output=$("$SCRIPT_DIR/generate_image.sh" "$@" 2>&1); then
  echo "$output" >&2
  exit 1
fi

# Echo the original output
echo "$output"

# Extract the image URL
image_url=$(echo "$output" | grep "^IMAGE_URL=" | head -1 | cut -d= -f2-)

if [[ -z "$image_url" ]]; then
  echo "Error: No image URL found in output" >&2
  exit 1
fi

# Generate a simple filename from task ID
task_id=$(echo "$output" | grep "^TASK_ID=" | cut -d= -f2-)
filename="generated_${task_id}.png"
temp_file="/tmp/${filename}"

# Download the image
if curl -sS "$image_url" -o "$temp_file"; then
  echo "PREVIEW_PATH=${temp_file}"
  echo ""
  echo "💡 You can download the original image from:"
  echo "$image_url"
else
  echo "Warning: Failed to download image for preview" >&2
fi

