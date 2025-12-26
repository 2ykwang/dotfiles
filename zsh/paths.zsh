# Homebrew (Apple Silicon: /opt/homebrew, Intel: /usr/local)
if [[ -f "/opt/homebrew/bin/brew" ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
elif [[ -f "/usr/local/bin/brew" ]]; then
    eval "$(/usr/local/bin/brew shellenv)"
fi

# Local bin
export PATH="$HOME/.local/bin:$PATH"

# pyenv
export PYENV_ROOT="$HOME/.pyenv"
[[ -d "$PYENV_ROOT/bin" ]] && export PATH="$PYENV_ROOT/bin:$PATH"
command -v pyenv >/dev/null && eval "$(pyenv init -)"

# libpq (PostgreSQL CLI)
[[ -d "${HOMEBREW_PREFIX}/opt/libpq/bin" ]] && export PATH="${HOMEBREW_PREFIX}/opt/libpq/bin:$PATH"
