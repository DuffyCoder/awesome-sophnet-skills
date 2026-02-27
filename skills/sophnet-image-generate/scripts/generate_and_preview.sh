#!/usr/bin/env bash
#
# Generate image and download for preview.
# Wrapper: calls generate_image.py via uv, downloads first result.
#
# Outputs:
#   TASK_ID=<id>
#   STATUS=succeeded
#   IMAGE_URL=<url>        (publicly accessible)
#   PREVIEW_PATH=<local path>
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
GEN_SCRIPT="${SCRIPT_DIR}/generate_image.py"

if [[ ! -f "$GEN_SCRIPT" ]]; then
  echo "Error: generate_image.py not found at ${GEN_SCRIPT}" >&2
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "Error: curl not found." >&2
  exit 1
fi

for arg in "$@"; do
  if [[ "$arg" == "-h" || "$arg" == "--help" ]]; then
    uv run --project "$SKILL_DIR" python "$GEN_SCRIPT" --help
    exit 0
  fi
done

if ! output="$(uv run --project "$SKILL_DIR" python "$GEN_SCRIPT" "$@" 2>&1)"; then
  echo "$output" >&2
  exit 1
fi

echo "$output"

# Python already downloads the image; check if PREVIEW_PATH was produced
preview_path="$(printf '%s\n' "$output" | awk '/^PREVIEW_PATH=/{print substr($0,14); exit}')"

if [[ -n "$preview_path" && -f "$preview_path" ]]; then
  exit 0
fi

# Fallback: download via curl if Python didn't produce a local file
image_url="$(printf '%s\n' "$output" | awk '/^IMAGE_URL=/{print substr($0,11); exit}')"

if [[ -z "$image_url" ]]; then
  echo "Error: No image URL found in output" >&2
  exit 1
fi

task_id="$(printf '%s\n' "$output" | awk '/^TASK_ID=/{print substr($0,9); exit}')"
: "${task_id:=$(date +%s)}"

path_no_query="${image_url%%\?*}"
ext="${path_no_query##*.}"
case "$ext" in
  jpg|jpeg|png|gif|webp|bmp) ;;
  *) ext="png" ;;
esac
temp_file="$(mktemp "/tmp/generated_${task_id}_XXXXXX.${ext}")"

if curl -fsSL "$image_url" -o "$temp_file"; then
  echo "PREVIEW_PATH=${temp_file}"
else
  rm -f "$temp_file"
  echo "Warning: Failed to download image for preview" >&2
fi
