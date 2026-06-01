# XDG config directory
ZSH_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/zsh"

# Load environment variables
source "$ZSH_CONFIG/environment.zsh"

# Load PATHs
source "$ZSH_CONFIG/paths.zsh"

# Load plugins (includes oh-my-zsh)
source "$ZSH_CONFIG/plugins.zsh"

# Load fzf (after oh-my-zsh for fzf-tab to work)
source "$ZSH_CONFIG/fzf.zsh"

# Load aliases
source "$ZSH_CONFIG/aliases.zsh"
[[ -f "$ZSH_CONFIG/aliases-secret.zsh" ]] && source "$ZSH_CONFIG/aliases-secret.zsh"

# Fortune with cowsay on terminal start
if command -v fortune &>/dev/null && command -v cowsay &>/dev/null; then
    fortune | cowsay
fi

eval "$(direnv hook zsh)"
