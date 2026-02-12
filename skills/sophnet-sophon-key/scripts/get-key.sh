#!/usr/bin/env bash
#
# sophon-key 配置脚本
# 从 Moltbot 配置文件获取 Sophon API Key 或提示用户设置环境变量
#

set -e

# 支持多个配置文件路径（按优先级查找）
MOLTBOT_CONFIG=""
for _cfg in "$HOME/.openclaw/openclaw.json" "$HOME/.clawdbot/moltbot.json" "$HOME/.moltbot/moltbot.json"; do
    if [[ -f "$_cfg" ]]; then
        MOLTBOT_CONFIG="$_cfg"
        break
    fi
done
# 默认回退路径
if [[ -z "$MOLTBOT_CONFIG" ]]; then
    MOLTBOT_CONFIG="$HOME/.openclaw/openclaw.json"
fi
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 颜色输出
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

# 从配置文件获取 Sophon API Key
get_api_key_from_config() {
    if [[ ! -f "$MOLTBOT_CONFIG" ]]; then
        log_warning "Moltbot 配置文件不存在: $MOLTBOT_CONFIG"
        return 1
    fi

    # 尝试使用 jq 解析配置文件
    if command -v jq &>/dev/null; then
        local api_key
        api_key=$(jq -r '.models.providers.sophnet.apiKey // empty' "$MOLTBOT_CONFIG" 2>/dev/null || true)

        if [[ -n "$api_key" && "$api_key" != "null" ]]; then
            echo "$api_key"
            return 0
        fi
    fi

    # 回退到 grep + sed 提取
    if command -v grep &>/dev/null && command -v sed &>/dev/null; then
        local api_key
        # 尝试匹配 "apiKey": "value" 格式（允许空格）
        api_key=$(grep '"apiKey"' "$MOLTBOT_CONFIG" | sed 's/.*"apiKey"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/' | head -1 || true)

        if [[ -n "$api_key" ]]; then
            echo "$api_key"
            return 0
        fi
    fi

    return 1
}

# 检查环境变量是否已设置
check_env_var() {
    if [[ -n "$SOPH_API_KEY" ]]; then
        # 环境变量已设置，静默返回
        return 0
    fi
    return 1
}

# 显示配置说明
show_config_help() {
    cat << EOF

${blue}Sophon API Key 配置${nc}

${yellow}方法 1: 手动设置环境变量${nc}
    export SOPH_API_KEY="your-api-key-here"

${yellow}方法 2: 添加到 shell 配置文件（推荐）${nc}
    echo 'export SOPH_API_KEY="your-api-key-here"' >> ~/.bashrc   # Bash
    echo 'export SOPH_API_KEY="your-api-key-here"' >> ~/.zshrc    # Zsh
    source ~/.bashrc   # 重新加载配置

${yellow}方法 3: 使用此脚本自动配置${nc}
    $SKILL_DIR/setup-key.sh

${yellow}方法 4: 从 Moltbot 配置文件自动获取${nc}
    脚本会自动从配置文件读取 API Key

EOF
}

# 解析命令行参数
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

# 主函数
main() {
    # 首先检查环境变量（静默）
    if check_env_var; then
        # 环境变量已设置
        if [[ "$OUTPUT_ONLY" == true ]]; then
            echo "$SOPH_API_KEY"
        fi
        return 0
    fi

    # 尝试从配置文件获取
    if [[ "$QUIET" != true ]]; then
        log_info "未找到 SOPH_API_KEY 环境变量，尝试从配置文件获取..."
    fi

    local api_key
    api_key=$(get_api_key_from_config)

    if [[ -n "$api_key" ]]; then
        if [[ "$QUIET" != true ]]; then
            log_success "从配置文件找到 Sophon API Key"
            echo -n "  值: "
            echo "${api_key:0:10}...${api_key: -5}"
            echo ""
        fi

        # 如果是只输出模式，打印 API KEY
        if [[ "$OUTPUT_ONLY" == true ]]; then
            echo "$api_key"
            return 0
        fi

        # 导出环境变量
        export SOPH_API_KEY="$api_key"
        if [[ "$QUIET" != true ]]; then
            log_success "已设置 SOPH_API_KEY 环境变量"
            log_info "建议: 将以下内容添加到您的 shell 配置文件 (~/.bashrc 或 ~/.zshrc):"
            echo "  export SOPH_API_KEY=\"$api_key\""
            echo ""
        fi
        return 0
    fi

    # 如果是只输出模式且静默，只返回错误
    if [[ "$OUTPUT_ONLY" == true ]]; then
        return 1
    fi

    # 未找到配置
    log_error "未找到 Sophon API Key 配置"
    show_config_help
    return 1
}

# 运行主函数
main "$@"