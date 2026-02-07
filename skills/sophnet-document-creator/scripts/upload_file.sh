#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  bash upload_file.sh --file "/path/to/file" [options]

Options:
  --file "/path/to/file"   Required. Local file path to upload.
  --api-key "KEY"          Optional. If omitted, resolve key automatically.
  --timeout 60              Optional. Curl timeout in seconds. Default: 60.
USAGE
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FILE_PATH=""
API_KEY=""
TIMEOUT="60"

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

if command -v realpath >/dev/null 2>&1; then
  ABS_FILE_PATH="$(realpath "$FILE_PATH")"
elif command -v readlink >/dev/null 2>&1; then
  ABS_FILE_PATH="$(readlink -f "$FILE_PATH")"
else
  ABS_FILE_PATH="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).expanduser().resolve())' "$FILE_PATH")"
fi

if [[ ! -f "$ABS_FILE_PATH" ]]; then
  echo "Error: file not found: $ABS_FILE_PATH" >&2
  exit 1
fi

if [[ -z "$API_KEY" ]]; then
  API_KEY="$(bash "$SCRIPT_DIR/resolve_api_key.sh" --output-quiet || true)"
fi

if [[ -z "$API_KEY" ]]; then
  echo "Error: No API key provided." >&2
  echo "Set SOPH_API_KEY or configure via sophnet-sophon-key." >&2
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "Error: curl not found." >&2
  exit 1
fi

response="$(curl -sS -X POST "https://www.sophnet.com/api/open-apis/projects/upload" \
  -H "Authorization: Bearer ${API_KEY}" \
  -F "file=@${ABS_FILE_PATH};type=application/octet-stream" \
  --max-time "$TIMEOUT")"

signed_url="$(printf '%s' "$response" | python3 -c 'import json,sys
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
echo "DOWNLOAD_URL=$signed_url"
