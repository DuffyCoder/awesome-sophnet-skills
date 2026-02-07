#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  bash upload_file.sh --file "/path/to/file.pptx" [options]

Options:
  --file "/path/to/file.pptx"   Required. Local file path to upload.
  --api-key "KEY"               Optional. If omitted, use SOPH_API_KEY when available.
  --timeout 60                  Optional. Curl timeout in seconds. Default: 60.
USAGE
}

FILE_PATH=""
API_KEY=""
TIMEOUT="60"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --file)
      FILE_PATH="$2"
      shift 2
      ;;
    --api-key)
      API_KEY="$2"
      shift 2
      ;;
    --timeout)
      TIMEOUT="$2"
      shift 2
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

if [[ -z "$API_KEY" ]]; then
  API_KEY="${SOPH_API_KEY:-}"
fi

if [[ -z "$API_KEY" ]]; then
  echo "FILE_PATH=$ABS_FILE_PATH"
  echo "UPLOAD_STATUS=skipped"
  echo "ERROR=missing_api_key"
  exit 0
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "Error: curl not found." >&2
  exit 1
fi

response="$(curl -sS -X POST "https://www.sophnet.com/api/open-apis/projects/upload" \
  -H "Authorization: Bearer ${API_KEY}" \
  -F "file=@${ABS_FILE_PATH};type=application/octet-stream" \
  --max-time "$TIMEOUT")"

signed_url="$(printf '%s' "$response" | uv run --project "$SKILL_DIR" python -c 'import json,sys
raw=sys.stdin.read().strip()
if not raw:
    sys.exit(1)
obj=json.loads(raw)
res=obj.get("result") if isinstance(obj,dict) else None
url=res.get("signedUrl") if isinstance(res,dict) else None
if not url:
    sys.exit(1)
print(url)
' 2>/dev/null || true)"

if [[ -z "$signed_url" ]]; then
  echo "Error: failed to parse signedUrl from upload response." >&2
  echo "$response" >&2
  exit 1
fi

echo "FILE_PATH=$ABS_FILE_PATH"
echo "UPLOAD_STATUS=uploaded"
echo "DOWNLOAD_URL=$signed_url"
