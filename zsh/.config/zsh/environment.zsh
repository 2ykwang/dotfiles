# Language
export LANG="ko_KR.UTF-8"

# GPG Signing Key
export GPG_TTY=$(tty)

# Lazygit (macOS defaults to ~/Library/Application Support, force XDG path)
export LG_CONFIG_FILE="$HOME/.config/lazygit/config.yml"
