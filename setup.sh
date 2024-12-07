#!/bin/sh

BASE_DIR="$( cd "$( dirname "$0" )" && pwd )"

# Homebrew install
echo "Checking and install brew if needed..."
if ! command -v brew &> /dev/null; then
  echo "brew not found. Installing..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
  echo "brew already installed."
fi

# install bundle packages from Brewfile
brew bundle --file=$BASE_DIR/Brewfile

# install zsh plugins
clone_plugin_if_needed() {
  local plugin_dir="$1"
  local repo_url="$2"
  local plugin_name=$(basename "$plugin_dir")

  if [ ! -d "$plugin_dir" ]; then
    echo "Cloning $plugin_name..."
    git clone "$repo_url" "$plugin_dir"
  else
    echo "$plugin_name already installed."
  fi
}

# Clone ZSH plugins
echo "Checking and cloning plugins if needed..."
clone_plugin_if_needed "$HOME/.oh-my-zsh/plugins/zsh-syntax-highlighting" "https://github.com/zsh-users/zsh-syntax-highlighting.git"
clone_plugin_if_needed "$HOME/.oh-my-zsh/plugins/zsh-autosuggestions" "https://github.com/zsh-users/zsh-autosuggestions.git"

# Link dotfiles
ln -sf $BASE_DIR/.zshrc $HOME/.zshrc
ln -sf $BASE_DIR/git/.gitignore $HOME/.gitignore

# run the Python script to configure user settings
python3 $BASE_DIR/configure.py

echo "Reloading shell..."
exec zsh
