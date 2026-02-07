#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_PYTHON="$SKILL_DIR/.venv/bin/python"
QUIET=false
FORCE_SYNC=false

usage() {
  cat <<'USAGE'
Usage:
  bash ensure_uv_env.sh [options]

Options:
  --quiet        Reduce non-error output.
  --force-sync   Force uv sync even when .venv already exists.
USAGE
}

log() {
  if [[ "$QUIET" != true ]]; then
    echo "$1" >&2
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --quiet)
      QUIET=true
      shift
      ;;
    --force-sync)
      FORCE_SYNC=true
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

if ! command -v uv >/dev/null 2>&1; then
  echo "Error: uv is required but not found." >&2
  echo "Install uv first: https://docs.astral.sh/uv/getting-started/installation/" >&2
  exit 1
fi

need_sync=false

if [[ "$FORCE_SYNC" == true || ! -x "$VENV_PYTHON" ]]; then
  need_sync=true
elif ! "$VENV_PYTHON" -c 'import defusedxml.minidom, lxml.etree' >/dev/null 2>&1; then
  need_sync=true
fi

if [[ "$need_sync" == true ]]; then
  log "Syncing uv environment at $SKILL_DIR/.venv"
  uv sync --project "$SKILL_DIR" --no-dev
else
  log "uv environment already ready: $SKILL_DIR/.venv"
fi
