export DOTFILES_DIR="$HOME/dotfiles"

# Load environment variables
source $DOTFILES_DIR/zsh/environment.zsh 
# Load aliases
source $DOTFILES_DIR/zsh/aliases.zsh
source $DOTFILES_DIR/zsh/aliases-secret.zsh
# Load PATHs
source $DOTFILES_DIR/zsh/paths.zsh 
# Load plugins
source $DOTFILES_DIR/zsh/plugins.zsh

# Load oh-my-zsh
source $ZSH/oh-my-zsh.sh
