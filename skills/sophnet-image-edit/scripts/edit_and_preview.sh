#!/usr/bin/env bash
#
# Edit image and download the first result for preview.
# Wrapper: calls edit_image.py via uv, downloads first result.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
EDIT_SCRIPT="${SCRIPT_DIR}/edit_image.py"

if [[ ! -f "$EDIT_SCRIPT" ]]; then
  echo "Error: edit_image.py not found at ${EDIT_SCRIPT}" >&2
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "Error: curl not found." >&2
  exit 1
fi

for arg in "$@"; do
  if [[ "$arg" == "-h" || "$arg" == "--help" ]]; then
    uv run --project "$SKILL_DIR" python "$EDIT_SCRIPT" --help
    exit 0
  fi
done

if ! output="$(uv run --project "$SKILL_DIR" python "$EDIT_SCRIPT" "$@" 2>&1)"; then
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
