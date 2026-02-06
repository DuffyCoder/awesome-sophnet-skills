#!/usr/bin/env bash
#
# sophnet-sophon-key setup script
# Help users configure Sophon API Key environment variable
#

set -e

MOLTBOT_CONFIG="${MOLTBOT_CONFIG:-$HOME/.clawdbot/moltbot.json}"

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
        return 1
    fi

    if command -v jq &>/dev/null; then
        local api_key
        api_key=$(jq -r '.models.providers.sophnet.apiKey // empty' "$MOLTBOT_CONFIG" 2>/dev/null || true)

        if [[ -n "$api_key" && "$api_key" != "null" ]]; then
            echo "$api_key"
            return 0
        fi
    fi

    if command -v grep &>/dev/null && command -v sed &>/dev/null; then
        local api_key
        api_key=$(grep '"apiKey"' "$MOLTBOT_CONFIG" | sed 's/.*"apiKey"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/' | head -1 || true)

        if [[ -n "$api_key" ]]; then
            echo "$api_key"
            return 0
        fi
    fi

    return 1
}

# Detect shell type
detect_shell() {
    if [[ -n "$ZSH_VERSION" ]]; then
        echo "zsh"
    elif [[ -n "$BASH_VERSION" ]]; then
        echo "bash"
    else
        # Detect default shell
        local shell
        shell=$(basename "$SHELL")
        echo "$shell"
    fi
}

# Get shell profile path
get_shell_rc() {
    local shell_type="$1"

    case "$shell_type" in
        zsh)
            echo "$HOME/.zshrc"
            ;;
        bash)
            echo "$HOME/.bashrc"
            ;;
        *)
            # Default
            echo "$HOME/.profile"
            ;;
    esac
}

# Add environment variable to shell profile
add_to_shell_rc() {
    local shell_rc="$1"
    local api_key="$2"

    # Check if already configured
    if grep -q "SOPH_API_KEY" "$shell_rc" 2>/dev/null; then
        log_warning "Detected existing SOPH_API_KEY in $shell_rc"
        read -p "Overwrite existing configuration? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Skipped configuration update"
            return 1
        fi

        # Remove old configuration
        sed -i '/^export SOPH_API_KEY=/d' "$shell_rc"
    fi

    # Add new configuration
    echo "" >> "$shell_rc"
    echo "# Sophon API Key (added by sophnet-sophon-key skill)" >> "$shell_rc"
    echo "export SOPH_API_KEY=\"$api_key\"" >> "$shell_rc"

    log_success "Added configuration to $shell_rc"
    return 0
}

# Main function
main() {
    echo ""
    echo -e "${blue}=== Sophon API Key Setup ===${nc}"
    echo ""

    # Detect shell type
    local shell_type
    shell_type=$(detect_shell)
    log_info "Detected shell: $shell_type"

    local shell_rc
    shell_rc=$(get_shell_rc "$shell_type")
    log_info "Profile file: $shell_rc"

    echo ""

    # Option 1: Resolve from config
    log_info "Option 1: Resolve from Moltbot config"
    local api_key
    api_key=$(get_api_key_from_config)

    if [[ -n "$api_key" ]]; then
        log_success "Found Sophon API Key"
        echo -n "  Value: "
        echo "${api_key:0:10}...${api_key: -5}"
        echo ""

        read -p "Use this API key? (Y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Nn]$ ]]; then
            api_key=""
        fi
    else
        log_warning "Sophon API Key not found in config"
        echo ""
    fi

    # Option 2: Manual input
    if [[ -z "$api_key" ]]; then
        log_info "Option 2: Enter API key manually"
        read -s "Enter your Sophon API Key: " api_key

        if [[ -z "$api_key" ]]; then
            log_error "API Key cannot be empty"
            exit 1
        fi
    fi

    echo ""
    log_info "Adding API key to environment configuration..."

    if add_to_shell_rc "$shell_rc" "$api_key"; then
        echo ""
        log_success "Setup complete!"
        echo ""
        log_info "Run this command to apply changes:"
        echo "  source $shell_rc"
        echo ""
        log_info "Or reopen your terminal"
        echo ""
    else
        log_warning "Configuration was not saved"
        exit 1
    fi
}

# Run main
main "$@"
