#!/bin/bash
#
# dotfiles setup script
# Usage: ./setup.sh [OPTIONS]
#
# Options:
#   --all       Run all setup steps (default if no option)
#   --link      Create symlinks only
#   --brew      Install Homebrew and packages only
#   --plugins   Install ZSH plugins only
#   --config    Run Git configuration only
#   --help      Show this help message
#

set -e

# Configuration
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
VERBOSE=${VERBOSE:-false}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging (printf for better compatibility)
log_info()    { printf "${BLUE}[INFO]${NC} %s\n" "$1"; }
log_success() { printf "${GREEN}[OK]${NC} %s\n" "$1"; }
log_warning() { printf "${YELLOW}[WARN]${NC} %s\n" "$1"; }
log_error()   { printf "${RED}[ERROR]${NC} %s\n" "$1"; }

error_exit() {
    log_error "$1"
    exit 1
}

# ============================================
# Link dotfiles
# ============================================
link_dotfiles() {
    log_info "Creating symlinks..."

    # Ensure directories exist
    mkdir -p "$HOME/.claude"
    mkdir -p "$HOME/.config/ghostty"
    mkdir -p "$HOME/.gnupg"
    chmod 700 "$HOME/.gnupg"

    # Define links: source|destination (using | as delimiter to avoid URL parsing issues)
    local links=(
        "$BASE_DIR/.vimrc|$HOME/.vimrc"
        "$BASE_DIR/.zshrc|$HOME/.zshrc"
        "$BASE_DIR/tmux/tmux.conf|$HOME/.tmux.conf"
        "$BASE_DIR/git/.gitignore|$HOME/.gitignore"
        "$BASE_DIR/claude/CLAUDE.md|$HOME/.claude/CLAUDE.md"
        "$BASE_DIR/claude/settings.json|$HOME/.claude/settings.json"
        "$BASE_DIR/claude/statusline-command.sh|$HOME/.claude/statusline-command.sh"
        "$BASE_DIR/claude/commands|$HOME/.claude/commands"
        "$BASE_DIR/ghostty/config|$HOME/.config/ghostty/config"
        "$BASE_DIR/gnupg/gpg-agent.conf|$HOME/.gnupg/gpg-agent.conf"
    )

    for link in "${links[@]}"; do
        local src="${link%%|*}"
        local dst="${link##*|}"

        if [[ -e "$src" ]]; then
            ln -sfn "$src" "$dst"
            log_success "Linked $(basename "$dst")"
        else
            log_warning "Source not found: $src"
        fi
    done
}

# ============================================
# Install Homebrew and packages
# ============================================
install_brew() {
    log_info "Checking Homebrew..."

    if ! command -v brew &>/dev/null; then
        log_info "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" \
            || error_exit "Failed to install Homebrew"

        # Add brew to PATH for Apple Silicon
        if [[ -f "/opt/homebrew/bin/brew" ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
        log_success "Homebrew installed"
    else
        log_success "Homebrew already installed"
    fi

    log_info "Installing packages from Brewfile..."
    brew bundle --file="$BASE_DIR/Brewfile" || error_exit "Failed to install packages"
    log_success "Packages installed"
}

# ============================================
# Install ZSH plugins
# ============================================
install_zsh_plugins() {
    log_info "Setting up ZSH plugins..."

    # Install Oh-My-Zsh if not present
    if [[ ! -d "$HOME/.oh-my-zsh" ]]; then
        log_info "Installing Oh-My-Zsh..."
        RUNZSH=no KEEP_ZSHRC=yes sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" \
            || error_exit "Failed to install Oh-My-Zsh"
        log_success "Oh-My-Zsh installed"
    else
        log_success "Oh-My-Zsh already installed"
    fi

    local plugins_dir="$HOME/.oh-my-zsh/custom/plugins"
    mkdir -p "$plugins_dir"

    # Plugin: name|url (using | as delimiter)
    local plugins=(
        "zsh-syntax-highlighting|https://github.com/zsh-users/zsh-syntax-highlighting.git"
        "zsh-autosuggestions|https://github.com/zsh-users/zsh-autosuggestions.git"
        "fzf-tab|https://github.com/Aloxaf/fzf-tab.git"
    )

    for plugin in "${plugins[@]}"; do
        local name="${plugin%%|*}"
        local url="${plugin##*|}"
        local dir="$plugins_dir/$name"

        if [[ ! -d "$dir" ]]; then
            log_info "Installing $name..."
            if git clone --depth=1 "$url" "$dir"; then
                log_success "$name installed"
            else
                log_warning "Failed to clone $name"
            fi
        else
            log_success "$name already installed"
        fi
    done
}

# ============================================
# Install Tmux plugins (TPM)
# ============================================
install_tmux_plugins() {
    log_info "Setting up Tmux plugins..."

    local tpm_dir="$HOME/.tmux/plugins/tpm"

    # Install TPM if not present
    if [[ ! -d "$tpm_dir" ]]; then
        log_info "Installing TPM (Tmux Plugin Manager)..."
        git clone --depth=1 https://github.com/tmux-plugins/tpm "$tpm_dir" \
            || error_exit "Failed to install TPM"
        log_success "TPM installed"
    else
        log_success "TPM already installed"
    fi

    # Install plugins if tmux is available
    if command -v tmux &>/dev/null; then
        log_info "Installing tmux plugins..."
        "$tpm_dir/bin/install_plugins" || log_warning "Failed to install tmux plugins"
        log_success "Tmux plugins installed"
    else
        log_warning "tmux not found, skipping plugin installation"
        log_info "Run 'prefix + I' in tmux to install plugins later"
    fi
}

# ============================================
# Install all plugins (ZSH + Tmux)
# ============================================
install_plugins() {
    install_zsh_plugins
    install_tmux_plugins
}

# ============================================
# Configure Git and personal settings
# ============================================
configure_git() {
    log_info "Setting up Git configuration..."

    # Set global gitignore (not a default, must be explicit)
    git config --global core.excludesfile ~/.gitignore

    # Ignore local changes to personal files
    git -C "$BASE_DIR" update-index --skip-worktree zsh/aliases-secret.zsh 2>/dev/null || true
    git -C "$BASE_DIR" update-index --skip-worktree CLAUDE.md 2>/dev/null || true

    # Run interactive configuration
    if [[ -f "$BASE_DIR/configure.py" ]]; then
        python3 "$BASE_DIR/configure.py"
    fi

    log_success "Git configuration complete"
}

# ============================================
# Show help
# ============================================
show_help() {
    cat << EOF
dotfiles setup script

Usage: ./setup.sh [OPTIONS]

Options:
  --all       Run all setup steps (default)
  --link      Create symlinks only
  --brew      Install Homebrew and packages only
  --plugins   Install ZSH plugins only
  --config    Run Git configuration only
  --help      Show this help message

Examples:
  ./setup.sh              # Full installation
  ./setup.sh --link       # Only create symlinks
  ./setup.sh --brew       # Only install packages
EOF
}

# ============================================
# Main
# ============================================
main() {
    local do_all=false
    local do_link=false
    local do_brew=false
    local do_plugins=false
    local do_config=false

    # Parse arguments
    if [[ $# -eq 0 ]]; then
        do_all=true
    fi

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --all)     do_all=true ;;
            --link)    do_link=true ;;
            --brew)    do_brew=true ;;
            --plugins) do_plugins=true ;;
            --config)  do_config=true ;;
            --help)    show_help; exit 0 ;;
            *)         log_error "Unknown option: $1"; show_help; exit 1 ;;
        esac
        shift
    done

    echo ""
    echo "================================"
    echo "  dotfiles setup"
    echo "================================"
    echo ""

    if $do_all || $do_link; then
        link_dotfiles
    fi

    if $do_all || $do_brew; then
        install_brew
    fi

    if $do_all || $do_plugins; then
        install_plugins
    fi

    if $do_all || $do_config; then
        configure_git
    fi

    echo ""
    log_success "Setup complete!"

    if $do_all; then
        log_info "Reloading shell..."
        exec zsh
    fi
}

main "$@"
