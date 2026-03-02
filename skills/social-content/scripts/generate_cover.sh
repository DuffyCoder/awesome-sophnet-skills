#!/usr/bin/env bash
#
# Generate image via SophNet Gemini API.
# Wrapper: calls generate_cover.py via uv.
# No local files are kept; only online URLs are produced.
#
# Required args:
#   --prompt "full prompt text"
#   --type   cover type (e.g. wechat-header, xiaohongshu)
#
# Outputs (stdout, machine-readable KEY=VALUE):
#   COVER_TYPE=<type>
#   COVER_SIZE=<W*H>
#   STATUS=succeeded
#   IMAGE_URL=<url>        (publicly accessible)
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
GEN_SCRIPT="${SCRIPT_DIR}/generate_cover.py"

if [[ ! -f "$GEN_SCRIPT" ]]; then
  echo "Error: generate_cover.py not found at ${GEN_SCRIPT}" >&2
  exit 1
fi

for arg in "$@"; do
  if [[ "$arg" == "-h" || "$arg" == "--help" ]]; then
    uv run --project "$SKILL_DIR" python "$GEN_SCRIPT" --help
    exit 0
  fi
done

if ! uv run --project "$SKILL_DIR" python "$GEN_SCRIPT" "$@"; then
  exit 1
fi
