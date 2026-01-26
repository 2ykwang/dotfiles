#!/bin/bash
# Create symlinks from config/links.txt

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib.sh"

BASE_DIR="$(get_base_dir)"
LINKS_FILE="$BASE_DIR/config/links.txt"

# Ensure required directories exist
ensure_dirs() {
    local dirs=(
        "$HOME/.claude"
        "$HOME/.config/ghostty"
        "$HOME/.gnupg"
    )

    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
    done

    # GPG requires strict permissions
    chmod 700 "$HOME/.gnupg"
}

# Create symlinks from links.txt
create_links() {
    info "Creating symlinks..."

    while IFS= read -r line || [[ -n "$line" ]]; do
        # Skip comments and empty lines
        [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue

        local src="${line%%|*}"
        local dst="${line##*|}"

        # Expand $HOME in destination
        dst="${dst//\$HOME/$HOME}"

        # Make source path absolute
        src="$BASE_DIR/$src"

        if [[ -e "$src" ]]; then
            ln -sfn "$src" "$dst"
            ok "$(basename "$dst")"
        else
            warn "Not found: $src"
        fi
    done < "$LINKS_FILE"
}

main() {
    ensure_dirs
    create_links
    ok "Symlinks created"
}

main
