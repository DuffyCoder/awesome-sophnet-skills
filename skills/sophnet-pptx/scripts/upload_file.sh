#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  bash upload_file.sh --file "/path/to/file.pptx" [options]

Options:
  --file "/path/to/file.pptx"   Required. Local file path to upload.
  --timeout 60                  Optional. Upload timeout in seconds. Default: 60.
  --url-only                    Optional. Print only URL when upload succeeds.
USAGE
}

FILE_PATH=""
TIMEOUT="60"
URL_ONLY="false"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --file)
      FILE_PATH="$2"
      shift 2
      ;;
    --timeout)
      TIMEOUT="$2"
      shift 2
      ;;
    --url-only)
      URL_ONLY="true"
      shift 1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$FILE_PATH" ]]; then
  echo "Error: --file is required." >&2
  exit 1
fi

bash "$SCRIPT_DIR/ensure_uv_env.sh" --quiet

if command -v realpath >/dev/null 2>&1; then
  ABS_FILE_PATH="$(realpath "$FILE_PATH")"
elif command -v readlink >/dev/null 2>&1; then
  ABS_FILE_PATH="$(readlink -f "$FILE_PATH")"
else
  ABS_FILE_PATH="$(uv run --project "$SKILL_DIR" python -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).expanduser().resolve())' "$FILE_PATH")"
fi

if [[ ! -f "$ABS_FILE_PATH" ]]; then
  echo "Error: file not found: $ABS_FILE_PATH" >&2
  exit 1
fi

if [[ "$ABS_FILE_PATH" != *.pptx ]]; then
  echo "Error: expected a .pptx file: $ABS_FILE_PATH" >&2
  exit 1
fi

signed_url="$(uv run --project "$SKILL_DIR" python -c "
import sophnet_tools, sys
u = sophnet_tools.upload_oss(sys.argv[1], timeout=int(sys.argv[2]))
print(u if u else '')
" "$ABS_FILE_PATH" "$TIMEOUT" 2>/dev/null || true)"

if [[ -z "$signed_url" ]]; then
  if [[ "$URL_ONLY" == "true" ]]; then
    echo "FILE_PATH=$ABS_FILE_PATH"
  else
    echo "FILE_PATH=$ABS_FILE_PATH"
    echo "UPLOAD_STATUS=skipped"
    echo "ERROR=upload_failed"
  fi
  exit 0
fi

if [[ "$URL_ONLY" == "true" ]]; then
  echo "$signed_url"
else
  echo "FILE_PATH=$ABS_FILE_PATH"
  echo "UPLOAD_STATUS=uploaded"
  echo "DOWNLOAD_URL=$signed_url"
fi
