#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  bash upload_file.sh --file "/path/to/file.xlsx" [options]

Options:
  --file "/path/to/file.xlsx"   Required. Local file path to upload.
  --api-key "KEY"               Optional. If omitted, use SOPH_API_KEY when available.
  --timeout 60                  Optional. Curl timeout in seconds. Default: 60.
  --url-only                    Optional. Print only URL when upload succeeds.
USAGE
}

FILE_PATH=""
API_KEY=""
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
    --api-key)
      API_KEY="$2"
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

if [[ "$ABS_FILE_PATH" != *.xlsx ]]; then
  echo "Error: expected an .xlsx file: $ABS_FILE_PATH" >&2
  exit 1
fi

if [[ -z "$API_KEY" ]]; then
  API_KEY="${SOPH_API_KEY:-}"
fi

# Fallback: delegate to sophon-key skill's get-key.sh
if [[ -z "$API_KEY" ]]; then
  SKILLS_DIR="$(cd "$SKILL_DIR/.." && pwd)"
  GET_KEY_SCRIPT=""
  for _candidate in "$SKILLS_DIR/sophon-key/scripts/get-key.sh" "$SKILLS_DIR/sophnet-sophon-key/scripts/get-key.sh"; do
    if [[ -f "$_candidate" ]]; then GET_KEY_SCRIPT="$_candidate"; break; fi
  done
  if [[ -n "$GET_KEY_SCRIPT" ]]; then
    API_KEY="$(bash "$GET_KEY_SCRIPT" --output-quiet 2>/dev/null || true)"
  fi
fi

if [[ -z "$API_KEY" ]]; then
  if [[ "$URL_ONLY" == "true" ]]; then
    echo "FILE_PATH=$ABS_FILE_PATH"
  else
    echo "FILE_PATH=$ABS_FILE_PATH"
    echo "UPLOAD_STATUS=skipped"
    echo "ERROR=missing_api_key"
  fi
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

if [[ "$URL_ONLY" == "true" ]]; then
  echo "$signed_url"
else
  echo "FILE_PATH=$ABS_FILE_PATH"
  echo "UPLOAD_STATUS=uploaded"
  echo "DOWNLOAD_URL=$signed_url"
fi
