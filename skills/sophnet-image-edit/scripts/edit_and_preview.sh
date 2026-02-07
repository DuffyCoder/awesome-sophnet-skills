#!/usr/bin/env bash
#
# Edit image and download the first result for preview.
# This wrapper script calls edit_image.sh and downloads the result.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EDIT_SCRIPT="${SCRIPT_DIR}/edit_image.sh"

if [[ ! -f "$EDIT_SCRIPT" ]]; then
  echo "Error: edit_image.sh not found at ${EDIT_SCRIPT}" >&2
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "Error: curl not found." >&2
  exit 1
fi

for arg in "$@"; do
  if [[ "$arg" == "-h" || "$arg" == "--help" ]]; then
    bash "$EDIT_SCRIPT" --help
    exit 0
  fi
done

if ! output="$(bash "$EDIT_SCRIPT" "$@" 2>&1)"; then
  echo "$output" >&2
  exit 1
fi

echo "$output"

image_url="$(printf '%s\n' "$output" | awk '/^IMAGE_URL=/{print substr($0,11); exit}')"
if [[ -z "$image_url" ]]; then
  echo "Error: No image URL found in output" >&2
  exit 1
fi

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

temp_file="$(mktemp "/tmp/edited_${task_id}_XXXXXX.${ext}")"

if curl -fsSL "$image_url" -o "$temp_file"; then
  echo "PREVIEW_PATH=${temp_file}"
else
  rm -f "$temp_file"
  echo "Warning: Failed to download image for preview" >&2
fi
