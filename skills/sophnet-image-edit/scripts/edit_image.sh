#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  bash edit_image.sh --prompt "text" --image "<url-or-local-path>" [options]

Options:
  --prompt "text"                 Required. Edit instruction prompt.
  --image "<url-or-local-path>"   Required at least once. Source image URL, data URI, or local file path. Repeatable.
  --images "a,b,c"                Optional. Comma-separated image refs (URL/data URI/local path).
  --images-file "/path/list.txt"  Optional. Read image refs from file, one per line.
  --model "Qwen-Image-Edit-2509"  Optional. Default: Qwen-Image-Edit-2509
  --size "1024*1024"              Optional. Default: 1024*1024
  --n 1                            Optional. Default: 1
  --watermark true|false           Optional. Default: false
  --api-key "KEY"                 Optional. If not set, uses SOPH_API_KEY.
  --poll-interval 2                Optional. Seconds between polls. Default: 2
  --max-wait 300                   Optional. Max seconds to wait. Default: 300
  --dry-run                        Optional. Validate and print input count only.
USAGE
}

json_escape() {
  printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' -e 's/\r/\\r/g' -e 's/\t/\\t/g' -e 's/\n/\\n/g'
}

to_bool() {
  local val
  val="$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')"
  case "$val" in
    true|1|yes|y)
      printf 'true'
      ;;
    false|0|no|n)
      printf 'false'
      ;;
    *)
      return 1
      ;;
  esac
}

validate_model() {
  case "$1" in
    Qwen-Image-Edit-2509)
      return 0
      ;;
    *)
      echo "Error: invalid --model '$1'. Must be: Qwen-Image-Edit-2509." >&2
      return 1
      ;;
  esac
}

require_positive_integer() {
  local val="$1"
  local flag="$2"
  case "$val" in
    ''|*[!0-9]*)
      echo "Error: invalid ${flag} (must be a positive integer)." >&2
      return 1
      ;;
  esac
  if (( val <= 0 )); then
    echo "Error: invalid ${flag} (must be > 0)." >&2
    return 1
  fi
}

extract_first_by_keys() {
  local resp="$1"
  shift
  local key val
  for key in "$@"; do
    val="$(printf '%s' "$resp" | grep -o "\"$key\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" | head -1 | sed -E 's/^"[^"]*"[[:space:]]*:[[:space:]]*"([^"]*)"/\1/')"
    if [[ -n "$val" ]]; then
      printf '%s' "$val"
      return 0
    fi
  done
  return 1
}

extract_all_urls() {
  local resp="$1"
  printf '%s' "$resp" | grep -o '"url"[[:space:]]*:[[:space:]]*"[^"]*"' | sed -E 's/^"url"[[:space:]]*:[[:space:]]*"([^"]*)"/\1/'
}

is_remote_image_ref() {
  case "$1" in
    http://*|https://*|data:image/*)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

mime_from_path() {
  local path="$1"
  local ext
  ext="$(printf '%s' "${path##*.}" | tr '[:upper:]' '[:lower:]')"
  case "$ext" in
    jpg|jpeg)
      printf 'image/jpeg'
      ;;
    png)
      printf 'image/png'
      ;;
    webp)
      printf 'image/webp'
      ;;
    gif)
      printf 'image/gif'
      ;;
    bmp)
      printf 'image/bmp'
      ;;
    avif)
      printf 'image/avif'
      ;;
    *)
      printf 'application/octet-stream'
      ;;
  esac
}

path_to_data_uri() {
  local path="$1"
  local mime b64
  mime="$(mime_from_path "$path")"
  b64="$(base64 < "$path" | tr -d '\n')"
  printf 'data:%s;base64,%s' "$mime" "$b64"
}

resolve_image_input() {
  local raw="$1"
  local path="$raw"

  if [[ "$path" == @* ]]; then
    path="${path#@}"
  fi

  if is_remote_image_ref "$path"; then
    printf '%s' "$path"
    return 0
  fi

  if [[ -f "$path" ]]; then
    if ! command -v base64 >/dev/null 2>&1; then
      echo "Error: base64 not found. Required for local image path input." >&2
      return 1
    fi
    path_to_data_uri "$path"
    return 0
  fi

  echo "Error: --image input not found: $raw" >&2
  echo "Hint: for uploaded files, use the resolved path from Media Understanding logs, usually under media/inbound/images/." >&2
  return 1
}

add_images_csv() {
  local raw_csv="$1"
  local old_ifs item
  old_ifs="$IFS"
  IFS=','
  # shellcheck disable=SC2206
  local parts=($raw_csv)
  IFS="$old_ifs"
  for item in "${parts[@]}"; do
    # Trim leading/trailing spaces.
    item="${item#"${item%%[![:space:]]*}"}"
    item="${item%"${item##*[![:space:]]}"}"
    [[ -n "$item" ]] && IMAGES+=("$item")
  done
}

add_images_file() {
  local file="$1"
  if [[ ! -f "$file" ]]; then
    echo "Error: --images-file not found: $file" >&2
    return 1
  fi

  local line
  while IFS= read -r line || [[ -n "$line" ]]; do
    # Strip trailing CR for Windows line endings and trim spaces.
    line="${line%$'\r'}"
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"
    [[ -z "$line" ]] && continue
    [[ "${line:0:1}" == "#" ]] && continue
    IMAGES+=("$line")
  done < "$file"
}

PROMPT=""
MODEL="Qwen-Image-Edit-2509"
SIZE="1024*1024"
N="1"
WATERMARK="false"
API_KEY=""
POLL_INTERVAL="2"
MAX_WAIT="300"
DRY_RUN="false"
IMAGES=()
PAYLOAD_FILE=""

cleanup_temp_files() {
  if [[ -n "${PAYLOAD_FILE:-}" && -f "$PAYLOAD_FILE" ]]; then
    rm -f "$PAYLOAD_FILE"
  fi
}

trap cleanup_temp_files EXIT

while [[ $# -gt 0 ]]; do
  case "$1" in
    --prompt)
      PROMPT="$2"
      shift 2
      ;;
    --image)
      IMAGES+=("$2")
      shift 2
      ;;
    --images)
      add_images_csv "$2"
      shift 2
      ;;
    --images-file)
      add_images_file "$2" || exit 1
      shift 2
      ;;
    --model)
      MODEL="$2"
      shift 2
      ;;
    --size)
      SIZE="$2"
      shift 2
      ;;
    --n)
      N="$2"
      shift 2
      ;;
    --watermark)
      WATERMARK="$2"
      shift 2
      ;;
    --api-key)
      API_KEY="$2"
      shift 2
      ;;
    --poll-interval)
      POLL_INTERVAL="$2"
      shift 2
      ;;
    --max-wait)
      MAX_WAIT="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN="true"
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

if [[ -z "$PROMPT" ]]; then
  echo "Error: --prompt is required." >&2
  exit 1
fi

if (( ${#IMAGES[@]} == 0 )); then
  echo "Error: at least one --image is required." >&2
  exit 1
fi

validate_model "$MODEL"
require_positive_integer "$N" "--n"
require_positive_integer "$POLL_INTERVAL" "--poll-interval"
require_positive_integer "$MAX_WAIT" "--max-wait"

prompt_esc="$(json_escape "$PROMPT")"

images_json=""
for img in "${IMAGES[@]}"; do
  resolved_img="$(resolve_image_input "$img")" || exit 1
  if [[ -n "$images_json" ]]; then
    images_json="${images_json},"
  fi
  images_json="${images_json}\"$(json_escape "$resolved_img")\""
done

params=""
if [[ -n "$SIZE" ]]; then
  size_esc="$(json_escape "$SIZE")"
  params="\"size\":\"${size_esc}\""
fi

if [[ -n "$N" ]]; then
  if [[ -n "$params" ]]; then params="${params},"; fi
  params="${params}\"n\":${N}"
fi

if [[ -n "$WATERMARK" ]]; then
  wm_bool="$(to_bool "$WATERMARK" || true)"
  if [[ -z "$wm_bool" ]]; then
    echo "Error: invalid --watermark (true/false)." >&2
    exit 1
  fi
  if [[ -n "$params" ]]; then params="${params},"; fi
  params="${params}\"watermark\":${wm_bool}"
fi

payload="{\"model\":\"${MODEL}\",\"input\":{\"prompt\":\"${prompt_esc}\",\"images\":[${images_json}]},\"parameters\":{${params}}}"

if [[ "$DRY_RUN" == "true" ]]; then
  echo "INPUT_IMAGE_COUNT=${#IMAGES[@]}"
  echo "STATUS=dry_run"
  exit 0
fi

# Check and load SOPH_API_KEY
if [[ -z "${API_KEY:-}" ]]; then
  API_KEY="${SOPH_API_KEY:-}"
fi

if [[ -z "${API_KEY:-}" ]]; then
  echo "Error: No API key provided." >&2
  echo "Please set SOPH_API_KEY environment variable or configure via sophnet-sophon-key skill." >&2
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "Error: curl not found." >&2
  exit 1
fi

PAYLOAD_FILE="$(mktemp "/tmp/sophnet_edit_payload_XXXXXX.json")"
printf '%s' "$payload" > "$PAYLOAD_FILE"

create_resp="$(curl -sS -X POST "https://www.sophnet.com/api/open-apis/projects/easyllms/imagegenerator/task" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  --data-binary "@${PAYLOAD_FILE}"
)"

if [[ -z "$create_resp" ]]; then
  echo "Error: empty response from create task API." >&2
  exit 1
fi

task_id="$(extract_first_by_keys "$create_resp" "task_id" "taskId" "taskID" "id" || true)"
if [[ -z "$task_id" ]]; then
  echo "Error: task_id not found in response." >&2
  echo "$create_resp" >&2
  exit 1
fi

echo "INPUT_IMAGE_COUNT=${#IMAGES[@]}"
echo "TASK_ID=${task_id}"

start_ts="$(date +%s)"
final_resp=""

while true; do
  now_ts="$(date +%s)"
  elapsed="$((now_ts - start_ts))"
  if (( elapsed > MAX_WAIT )); then
    echo "Error: timed out after ${MAX_WAIT}s." >&2
    exit 1
  fi

  status_resp="$(curl -sS -X GET "https://www.sophnet.com/api/open-apis/projects/easyllms/imagegenerator/task/${task_id}" \
    -H "Authorization: Bearer ${API_KEY}"
  )"

  status="$(extract_first_by_keys "$status_resp" "status" "taskStatus" "task_status" || true)"
  status_norm="$(printf "%s" "$status" | tr '[:upper:]' '[:lower:]')"

  if [[ "$status_norm" == "succeeded" || "$status_norm" == "success" ]]; then
    final_resp="$status_resp"
    echo "STATUS=succeeded"
    break
  fi

  if [[ "$status_norm" == "failed" || "$status_norm" == "error" ]]; then
    echo "STATUS=failed" >&2
    echo "$status_resp" >&2
    exit 1
  fi

  sleep "$POLL_INTERVAL"
done

urls="$(extract_all_urls "$final_resp" || true)"
if [[ -z "$urls" ]]; then
  echo "Error: url not found in response." >&2
  echo "$final_resp" >&2
  exit 1
fi

while IFS= read -r u; do
  [[ -n "$u" ]] && echo "IMAGE_URL=${u}"
done <<<"$urls"
