#!/bin/bash
# Install Homebrew and packages from Brewfile

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib.sh"

BASE_DIR="$(get_base_dir)"

install_homebrew() {
    if command -v brew &>/dev/null; then
        ok "Homebrew already installed"
        return
    fi

    info "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" \
        || die "Failed to install Homebrew"

    # Add to PATH for Apple Silicon
    if [[ -f "/opt/homebrew/bin/brew" ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi

    ok "Homebrew installed"
}

install_packages() {
    info "Installing packages from Brewfile..."
    brew bundle install --file="$BASE_DIR/Brewfile" \
        || die "Failed to install packages"
    ok "Packages installed"
}

main() {
    install_homebrew
    install_packages
}

main
