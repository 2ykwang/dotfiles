#!/bin/bash
# Install ZSH, Tmux and Herdr plugins

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib.sh"

# ZSH plugins to install: name|url
ZSH_PLUGINS=(
    "zsh-syntax-highlighting|https://github.com/zsh-users/zsh-syntax-highlighting.git"
    "zsh-autosuggestions|https://github.com/zsh-users/zsh-autosuggestions.git"
    "fzf-tab|https://github.com/Aloxaf/fzf-tab.git"
)

install_omz() {
    if [[ -d "$HOME/.oh-my-zsh" ]]; then
        ok "Oh-My-Zsh already installed"
        return
    fi

    info "Installing Oh-My-Zsh..."
    RUNZSH=no KEEP_ZSHRC=yes sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" \
        || die "Failed to install Oh-My-Zsh"
    ok "Oh-My-Zsh installed"
}

install_zsh_plugins() {
    local plugins_dir="$HOME/.oh-my-zsh/custom/plugins"
    mkdir -p "$plugins_dir"

    for plugin in "${ZSH_PLUGINS[@]}"; do
        local name="${plugin%%|*}"
        local url="${plugin##*|}"
        local dir="$plugins_dir/$name"

        if [[ -d "$dir" ]]; then
            ok "$name already installed"
        else
            info "Installing $name..."
            if git clone --depth=1 "$url" "$dir" 2>/dev/null; then
                ok "$name installed"
            else
                warn "Failed to install $name"
            fi
        fi
    done
}

install_tpm() {
    local tpm_dir="$HOME/.tmux/plugins/tpm"

    if [[ -d "$tpm_dir" ]]; then
        ok "TPM already installed"
        return
    fi

    info "Installing TPM..."
    git clone --depth=1 https://github.com/tmux-plugins/tpm "$tpm_dir" \
        || die "Failed to install TPM"
    ok "TPM installed"
}

install_tmux_plugins() {
    local tpm_dir="$HOME/.tmux/plugins/tpm"

    if ! command -v tmux &>/dev/null; then
        warn "tmux not found, skipping plugin install"
        info "Run 'prefix + I' in tmux later"
        return
    fi

    info "Installing tmux plugins..."
    "$tpm_dir/bin/install_plugins" 2>/dev/null || warn "Plugin install failed"
    ok "Tmux plugins installed"
}

herdr_plugin_registered() {
    herdr plugin list --plugin "$1" --json 2>/dev/null | grep -q "\"plugin_id\":\"$1\""
}

# Herdr keeps its plugin registry in ~/.config/herdr/plugins.json, which stow
# does not manage, so config.toml can reference plugins that were never
# registered on this machine.
install_herdr_plugins() {
    if ! command -v herdr &>/dev/null; then
        warn "herdr not found, skipping Herdr plugins"
        return
    fi

    # `herdr plugin install` replaces an existing registration, including one
    # linked from a local checkout, so only install when the id is missing.
    if herdr_plugin_registered herdr-finder; then
        ok "herdr-finder already registered"
    elif herdr plugin install 2ykwang/herdr-finder --yes >/dev/null; then
        ok "herdr-finder installed"
    else
        warn "Failed to install herdr-finder"
    fi

    local sidebar_dir
    sidebar_dir="$(get_base_dir)/herdr/.config/herdr/local-plugins/sidebar-activity"
    if herdr_plugin_registered sidebar-activity; then
        ok "sidebar-activity already registered"
    elif herdr plugin link "$sidebar_dir" >/dev/null; then
        ok "sidebar-activity linked"
    else
        warn "Failed to link sidebar-activity"
    fi
}

main() {
    info "Setting up ZSH plugins..."
    install_omz
    install_zsh_plugins

    info "Setting up Tmux plugins..."
    install_tpm
    install_tmux_plugins

    info "Setting up Herdr plugins..."
    install_herdr_plugins
}

main
