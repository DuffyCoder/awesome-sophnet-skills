#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
SOPHON_KEY_SCRIPT="$SKILLS_DIR/sophnet-sophon-key/scripts/get-key.sh"

OUTPUT_ONLY=false
QUIET=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output)
      OUTPUT_ONLY=true
      shift
      ;;
    --quiet)
      QUIET=true
      shift
      ;;
    --output-quiet)
      OUTPUT_ONLY=true
      QUIET=true
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

get_api_key_from_config_file() {
  local config_path="$1"

  if [[ ! -f "$config_path" ]]; then
    return 1
  fi

  if command -v jq >/dev/null 2>&1; then
    local api_key
    api_key="$(jq -r '.models.providers.sophnet.apiKey // .models.providers.sophnet.api_key // empty' "$config_path" 2>/dev/null || true)"
    if [[ -n "$api_key" && "$api_key" != "null" ]]; then
      printf '%s' "$api_key"
      return 0
    fi
  fi

  if command -v grep >/dev/null 2>&1 && command -v sed >/dev/null 2>&1; then
    local api_key
    api_key="$(grep -E '"apiKey"|"api_key"' "$config_path" | sed 's/.*"apiKey"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/; s/.*"api_key"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/' | head -1 || true)"
    if [[ -n "$api_key" ]]; then
      printf '%s' "$api_key"
      return 0
    fi
  fi

  return 1
}

get_api_key_from_configs() {
  local config_paths=()
  local candidate

  if [[ -n "${MOLTBOT_CONFIG:-}" ]]; then
    config_paths+=("$MOLTBOT_CONFIG")
  fi

  config_paths+=(
    "$HOME/.clawdbot/moltbot.json"
    "$HOME/.moltbot/moltbot.json"
    "$HOME/.openclaw/openclaw.json"
  )

  for candidate in "${config_paths[@]}"; do
    local api_key
    api_key="$(get_api_key_from_config_file "$candidate" || true)"
    if [[ -n "$api_key" ]]; then
      printf '%s' "$api_key"
      return 0
    fi
  done

  return 1
}

emit_key() {
  local key="$1"
  if [[ "$OUTPUT_ONLY" == true ]]; then
    printf '%s\n' "$key"
  elif [[ "$QUIET" != true ]]; then
    echo "Resolved SOPH_API_KEY"
  fi
}

main() {
  if [[ -n "${SOPH_API_KEY:-}" ]]; then
    emit_key "$SOPH_API_KEY"
    return 0
  fi

  if [[ -f "$SOPHON_KEY_SCRIPT" ]]; then
    local resolved
    resolved="$(bash "$SOPHON_KEY_SCRIPT" --output-quiet 2>/dev/null || true)"
    if [[ -n "$resolved" ]]; then
      emit_key "$resolved"
      return 0
    fi
  fi

  local config_key
  config_key="$(get_api_key_from_configs || true)"
  if [[ -n "$config_key" ]]; then
    emit_key "$config_key"
    return 0
  fi

  if [[ "$OUTPUT_ONLY" == true ]]; then
    return 1
  fi

  echo "Error: No Sophnet API key available." >&2
  echo "Set SOPH_API_KEY or run the sophnet-sophon-key skill to configure credentials." >&2
  return 1
}

main "$@"
