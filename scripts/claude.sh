#!/bin/bash
# Install Claude Code with the official native installer

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib.sh"

install_claude() {
    # The native installer puts the launcher at ~/.local/bin/claude, which may
    # not be on PATH until the shell restarts.
    if command -v claude &>/dev/null || [[ -x "$HOME/.local/bin/claude" ]]; then
        ok "Claude Code already installed"
        return
    fi

    info "Installing Claude Code..."
    curl -fsSL https://claude.ai/install.sh | bash \
        || die "Failed to install Claude Code"
    ok "Claude Code installed"
}

main() {
    install_claude
}

main
