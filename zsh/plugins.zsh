# Plugins
plugins=(
    git 
    alias-tips 
    zsh-autosuggestions 
    zsh-syntax-highlighting 
    poetry 
    zsh-interactive-cd 
    alias-finder
)

zstyle ':omz:plugins:alias-finder' autoload yes

# 플러그인 초기화
source ~/.oh-my-zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
source ~/.oh-my-zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh

# Source oh-my-zsh 
export ZSH_THEME="nicoulaj"
export ZSH="$HOME/.oh-my-zsh" 
