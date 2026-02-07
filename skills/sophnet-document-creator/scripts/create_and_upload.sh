#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  bash create_and_upload.sh --type docx|pptx --title "Title" [options]

Options:
  --type docx|pptx         Required.
  --title "text"           Required.
  --content "text"         Optional inline markdown/plain text.
  --markdown "/path.md"    Optional markdown source.
  --author "name"          Optional DOCX author label.
  --slides 6               Optional PPTX slide count.
  --output "/path.ext"     Optional output path (requires --keep-local or --no-upload).
  --api-key "KEY"          Optional upload API key.
  --no-upload              Optional. Create file only (requires --keep-local).
  --keep-local             Optional. Keep generated file on disk.
USAGE
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DOC_TYPE=""
TITLE=""
CONTENT=""
MARKDOWN=""
AUTHOR=""
SLIDES=""
OUTPUT=""
API_KEY=""
UPLOAD="true"
KEEP_LOCAL="false"
GENERATED_FILE=""
AUTO_CLEANUP="false"

cleanup_generated_file() {
  if [[ "$AUTO_CLEANUP" == "true" && -n "$GENERATED_FILE" && -f "$GENERATED_FILE" ]]; then
    rm -f "$GENERATED_FILE"
  fi
}

trap cleanup_generated_file EXIT

while [[ $# -gt 0 ]]; do
  case "$1" in
    --type)
      DOC_TYPE="$2"
      shift 2
      ;;
    --title)
      TITLE="$2"
      shift 2
      ;;
    --content)
      CONTENT="$2"
      shift 2
      ;;
    --markdown)
      MARKDOWN="$2"
      shift 2
      ;;
    --author)
      AUTHOR="$2"
      shift 2
      ;;
    --slides)
      SLIDES="$2"
      shift 2
      ;;
    --output)
      OUTPUT="$2"
      shift 2
      ;;
    --api-key)
      API_KEY="$2"
      shift 2
      ;;
    --no-upload)
      UPLOAD="false"
      shift
      ;;
    --keep-local)
      KEEP_LOCAL="true"
      shift
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

if [[ -z "$DOC_TYPE" || -z "$TITLE" ]]; then
  echo "Error: --type and --title are required." >&2
  usage
  exit 1
fi

if [[ "$UPLOAD" == "false" && "$KEEP_LOCAL" != "true" ]]; then
  echo "Error: --no-upload requires --keep-local." >&2
  exit 1
fi

if [[ -n "$OUTPUT" && "$UPLOAD" == "true" && "$KEEP_LOCAL" != "true" ]]; then
  echo "Error: --output requires --keep-local when upload is enabled." >&2
  exit 1
fi

if [[ -z "$OUTPUT" && "$UPLOAD" == "true" && "$KEEP_LOCAL" != "true" ]]; then
  OUTPUT="$(mktemp "/tmp/sophnet_document_${DOC_TYPE}_XXXXXX.${DOC_TYPE}")"
  AUTO_CLEANUP="true"
fi

if [[ "$UPLOAD" == "true" && -z "$API_KEY" ]]; then
  API_KEY="$(bash "$SCRIPT_DIR/resolve_api_key.sh" --output-quiet || true)"
  if [[ -z "$API_KEY" ]]; then
    echo "UPLOAD_STATUS=failed"
    echo "ERROR=missing_api_key"
    echo "Error: No API key provided." >&2
    echo "Set SOPH_API_KEY, pass --api-key, or configure via sophnet-sophon-key." >&2
    exit 1
  fi
fi

bash "$SCRIPT_DIR/ensure_uv_env.sh" --quiet
VENV_PYTHON="$SKILL_DIR/.venv/bin/python"

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "Error: uv environment is not ready: $VENV_PYTHON" >&2
  exit 1
fi

create_cmd=("$VENV_PYTHON" "$SCRIPT_DIR/create_document.py" "$DOC_TYPE" --title "$TITLE")

if [[ -n "$CONTENT" ]]; then
  create_cmd+=(--content "$CONTENT")
fi
if [[ -n "$MARKDOWN" ]]; then
  create_cmd+=(--markdown "$MARKDOWN")
fi
if [[ -n "$AUTHOR" ]]; then
  create_cmd+=(--author "$AUTHOR")
fi
if [[ -n "$SLIDES" ]]; then
  create_cmd+=(--slides "$SLIDES")
fi
if [[ -n "$OUTPUT" ]]; then
  create_cmd+=(--output "$OUTPUT")
fi

create_output="$("${create_cmd[@]}")"

file_path="$(printf '%s\n' "$create_output" | awk -F= '/^FILE_PATH=/{print substr($0,11); exit}')"
file_type="$(printf '%s\n' "$create_output" | awk -F= '/^FILE_TYPE=/{print substr($0,11); exit}')"
file_name="$(printf '%s\n' "$create_output" | awk -F= '/^FILE_NAME=/{print substr($0,11); exit}')"

if [[ -z "$file_path" ]]; then
  echo "Error: FILE_PATH not found in create output." >&2
  exit 1
fi

GENERATED_FILE="$file_path"

if [[ -n "$file_type" ]]; then
  echo "FILE_TYPE=$file_type"
fi
if [[ -n "$file_name" ]]; then
  echo "FILE_NAME=$file_name"
fi

if [[ "$UPLOAD" == "false" ]]; then
  echo "UPLOAD_STATUS=skipped"
  echo "FILE_PATH=$file_path"
  exit 0
fi

upload_cmd=(bash "$SCRIPT_DIR/upload_file.sh" --file "$file_path" --api-key "$API_KEY")

upload_output=""
if ! upload_output="$("${upload_cmd[@]}" 2>&1)"; then
  echo "UPLOAD_STATUS=failed"
  echo "ERROR=upload_failed"
  echo "$upload_output" >&2
  exit 1
fi

download_url="$(printf '%s\n' "$upload_output" | awk -F= '/^DOWNLOAD_URL=/{print substr($0,14); exit}')"
if [[ -z "$download_url" ]]; then
  download_url="$(printf '%s\n' "$upload_output" | awk -F= '/^SIGNED_URL=/{print substr($0,12); exit}')"
fi
if [[ -z "$download_url" ]]; then
  echo "UPLOAD_STATUS=failed"
  echo "ERROR=missing_download_url"
  echo "Error: DOWNLOAD_URL not found in upload output." >&2
  echo "$upload_output" >&2
  exit 1
fi

echo "UPLOAD_STATUS=uploaded"
echo "DOWNLOAD_URL=$download_url"

if [[ "$KEEP_LOCAL" == "true" ]]; then
  echo "FILE_PATH=$file_path"
else
  cleanup_generated_file
  AUTO_CLEANUP="false"
  echo "LOCAL_FILE_STATUS=deleted"
fi
