# Oh-My-Zsh configuration
export ZSH="$HOME/.oh-my-zsh"
export ZSH_THEME="nicoulaj"

# Plugins (loaded by oh-my-zsh)
plugins=(
    git
    zsh-autosuggestions
    zsh-syntax-highlighting
    zsh-interactive-cd
    alias-finder
)

# Plugin settings
zstyle ':omz:plugins:alias-finder' autoload yes

# Load Oh-My-Zsh
[[ -f "$ZSH/oh-my-zsh.sh" ]] && source "$ZSH/oh-my-zsh.sh"
