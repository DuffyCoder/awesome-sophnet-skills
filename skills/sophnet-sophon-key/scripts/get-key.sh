#!/usr/bin/env bash
#
# sophnet-sophon-key configuration script
# Resolve Sophon API Key from Moltbot config or guide env setup
#

set -e

# 支持多个配置文件路径
MOLTBOT_CONFIG=""
if [[ -f "$HOME/.clawdbot/moltbot.json" ]]; then
    MOLTBOT_CONFIG="$HOME/.clawdbot/moltbot.json"
elif [[ -f "$HOME/.moltbot/moltbot.json" ]]; then
    MOLTBOT_CONFIG="$HOME/.moltbot/moltbot.json"
else
    MOLTBOT_CONFIG="$HOME/.clawdbot/moltbot.json"
fi
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colored output
green='\033[0;32m'
yellow='\033[1;33m'
red='\033[0;31m'
blue='\033[0;34m'
nc='\033[0m'

log_info() {
    echo -e "${blue}ℹ${nc} $1"
}

log_success() {
    echo -e "${green}✓${nc} $1"
}

log_warning() {
    echo -e "${yellow}⚠${nc} $1"
}

log_error() {
    echo -e "${red}✗${nc} $1"
}

# Get Sophon API Key from config
get_api_key_from_config() {
    if [[ ! -f "$MOLTBOT_CONFIG" ]]; then
        log_warning "Moltbot config file does not exist: $MOLTBOT_CONFIG"
        return 1
    fi

    # Try parsing config with jq
    if command -v jq &>/dev/null; then
        local api_key
        api_key=$(jq -r '.models.providers.sophnet.apiKey // empty' "$MOLTBOT_CONFIG" 2>/dev/null || true)

        if [[ -n "$api_key" && "$api_key" != "null" ]]; then
            echo "$api_key"
            return 0
        fi
    fi

    # Fallback: extract with grep + sed
    if command -v grep &>/dev/null && command -v sed &>/dev/null; then
        local api_key
        # Match "apiKey": "value" format (allowing spaces)
        api_key=$(grep '"apiKey"' "$MOLTBOT_CONFIG" | sed 's/.*"apiKey"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/' | head -1 || true)

        if [[ -n "$api_key" ]]; then
            echo "$api_key"
            return 0
        fi
    fi

    return 1
}

# Check whether env var is already set
check_env_var() {
    if [[ -n "$SOPH_API_KEY" ]]; then
        # Env var is already set; return silently
        return 0
    fi
    return 1
}

# Show configuration help
show_config_help() {
    cat << EOF

${blue}Sophon API Key Configuration${nc}

${yellow}Method 1: Set environment variable manually${nc}
    export SOPH_API_KEY="your-api-key-here"

${yellow}Method 2: Add to shell profile (recommended)${nc}
    echo 'export SOPH_API_KEY="your-api-key-here"' >> ~/.bashrc   # Bash
    echo 'export SOPH_API_KEY="your-api-key-here"' >> ~/.zshrc    # Zsh
    source ~/.bashrc   # Reload configuration

${yellow}Method 3: Use this script for automatic setup${nc}
    $SKILL_DIR/setup-key.sh

${yellow}Method 4: Resolve automatically from Moltbot config${nc}
    This script will read API key from config automatically

EOF
}

# Parse command-line arguments
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
      shift
      ;;
  esac
done

# Main function
main() {
    # Check env var first (silent)
    if check_env_var; then
        # Env var is already set
        if [[ "$OUTPUT_ONLY" == true ]]; then
            echo "$SOPH_API_KEY"
        fi
        return 0
    fi

    # Try resolving from config
    if [[ "$QUIET" != true ]]; then
        log_info "SOPH_API_KEY is not set, trying to resolve from config..."
    fi

    local api_key
    api_key=$(get_api_key_from_config)

    if [[ -n "$api_key" ]]; then
        if [[ "$QUIET" != true ]]; then
            log_success "Found Sophon API Key in config"
            echo -n "  Value: "
            echo "${api_key:0:10}...${api_key: -5}"
            echo ""
        fi

        # Output-only mode: print API key
        if [[ "$OUTPUT_ONLY" == true ]]; then
            echo "$api_key"
            return 0
        fi

        # Export env var
        export SOPH_API_KEY="$api_key"
        if [[ "$QUIET" != true ]]; then
            log_success "Set SOPH_API_KEY environment variable"
            log_info "Tip: add this line to your shell profile (~/.bashrc or ~/.zshrc):"
            echo "  export SOPH_API_KEY=\"$api_key\""
            echo ""
        fi
        return 0
    fi

    # Output-only mode: return error only
    if [[ "$OUTPUT_ONLY" == true ]]; then
        return 1
    fi

    # Not found in any source
    log_error "Sophon API Key configuration not found"
    show_config_help
    return 1
}

# Run main
main "$@"
