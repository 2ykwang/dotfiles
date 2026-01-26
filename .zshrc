export DOTFILES_DIR="$HOME/dotfiles"

# Load environment variables
source "$DOTFILES_DIR/zsh/environment.zsh"

# Load PATHs
source "$DOTFILES_DIR/zsh/paths.zsh"

# Load plugins (includes oh-my-zsh)
source "$DOTFILES_DIR/zsh/plugins.zsh"

# Load fzf (after oh-my-zsh for fzf-tab to work)
source "$DOTFILES_DIR/zsh/fzf.zsh"

# Load aliases
source "$DOTFILES_DIR/zsh/aliases.zsh"
[[ -f "$DOTFILES_DIR/zsh/aliases-secret.zsh" ]] && source "$DOTFILES_DIR/zsh/aliases-secret.zsh"

# Fortune with cowsay on terminal start (async)
if command -v fortune &> /dev/null && command -v cowsay &> /dev/null; then
    { fortune | cowsay } &!
fi
