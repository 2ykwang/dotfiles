#!/bin/bash
#
# dotfiles setup - modular installer
#
# Usage:
#   ./setup.sh [command]
#
# Commands:
#   all       Run all setup steps
#   link      Create symlinks only
#   brew      Install Homebrew and packages
#   plugins   Install ZSH/Tmux plugins
#   help      Show this help (default)
#

set -e

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$BASE_DIR/scripts/lib.sh"

# Git configuration (skip-worktree for personal files)
configure_git() {
    git config --global core.excludesfile ~/.gitignore
    git -C "$BASE_DIR" update-index --skip-worktree zsh/aliases-secret.zsh 2>/dev/null || true
}

show_help() {
    cat << 'EOF'
dotfiles setup

Usage: ./setup.sh [command]

Commands:
  all       Run all setup steps
  link      Create symlinks only
  brew      Install Homebrew and packages
  plugins   Install ZSH/Tmux plugins
  help      Show this help (default)

Examples:
  ./setup.sh all      # Full install
  ./setup.sh link     # Symlinks only
  ./setup.sh brew     # Packages only
EOF
}

main() {
    local cmd="${1:-help}"

    echo ""
    echo "================================"
    echo "  dotfiles setup"
    echo "================================"
    echo ""

    case "$cmd" in
        all)
            "$BASE_DIR/scripts/link.sh"
            "$BASE_DIR/scripts/brew.sh"
            "$BASE_DIR/scripts/plugins.sh"
            configure_git
            ok "Setup complete!"
            info "Restart your shell or run: exec zsh"
            ;;
        link)
            "$BASE_DIR/scripts/link.sh"
            ;;
        brew)
            "$BASE_DIR/scripts/brew.sh"
            ;;
        plugins)
            "$BASE_DIR/scripts/plugins.sh"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            err "Unknown command: $cmd"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
