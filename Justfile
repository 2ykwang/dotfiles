# dotfiles

set shell := ["bash", "-cu"]

packages := "zsh vim tmux git ghostty gnupg claude lazygit"

# Show available commands
default:
    @just --list

# Run all setup steps
all: brew link plugins configure
    @echo "Setup complete! Restart your shell or run: exec zsh"

# Create symlinks using GNU Stow
link:
    @mkdir -p ~/.config/zsh ~/.config/ghostty ~/.config/lazygit ~/.gnupg ~/.claude
    @chmod 700 ~/.gnupg
    @for pkg in {{ packages }}; do stow -v --restow "$pkg"; done
    @sed -i '' "s|pinentry-program .*|pinentry-program $(brew --prefix)/bin/pinentry-mac|" gnupg/.gnupg/gpg-agent.conf
    @echo "Symlinks created"

# Remove symlinks
unlink:
    @for pkg in {{ packages }}; do stow -v --delete "$pkg"; done
    @echo "Symlinks removed"

# Install Homebrew and packages
brew:
    @bash scripts/brew.sh

# Install ZSH and Tmux plugins
plugins:
    @bash scripts/plugins.sh

# Configure git user settings (interactive)
configure:
    @bash scripts/configure.sh
