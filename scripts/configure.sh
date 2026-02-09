#!/bin/bash
# Interactive git user configuration

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib.sh"

configure_gpg_key() {
    # Collect GPG key IDs and emails
    local keys=()
    local emails=()

    while IFS= read -r line; do
        if [[ "$line" =~ ^sec ]]; then
            local key_id
            key_id=$(echo "$line" | sed 's/.*\/\([A-F0-9]*\) .*/\1/')
            keys+=("$key_id")
        elif [[ "$line" =~ ^uid ]]; then
            local email
            email=$(echo "$line" | sed 's/.*<\(.*\)>.*/\1/')
            emails+=("$email")
        fi
    done < <(gpg --list-secret-keys --keyid-format long 2>/dev/null)

    if [[ ${#keys[@]} -eq 0 ]]; then
        warn "No GPG keys found, skipping signing key setup"
        return
    fi

    info "Available GPG keys:"
    for i in "${!keys[@]}"; do
        echo "  $((i + 1))) ${keys[$i]}  ${emails[$i]}"
    done
    echo "  0) Skip"

    local choice
    read -rp "Select key [1]: " choice
    choice="${choice:-1}"

    if [[ "$choice" == "0" ]]; then
        info "Skipped GPG signing key"
        return
    fi

    local idx=$((choice - 1))
    if [[ $idx -lt 0 || $idx -ge ${#keys[@]} ]]; then
        warn "Invalid selection, skipping"
        return
    fi

    git config --global user.signingkey "${keys[$idx]}"
    ok "GPG signing key: ${keys[$idx]} (${emails[$idx]})"
}

configure_git() {
    info "Configuring git settings..."

    local current_name current_email
    current_name=$(git config --global user.name 2>/dev/null || true)
    current_email=$(git config --global user.email 2>/dev/null || true)

    read -rp "Git username [${current_name}]: " git_username
    read -rp "Git email [${current_email}]: " git_email

    git_username="${git_username:-$current_name}"
    git_email="${git_email:-$current_email}"

    [[ -z "$git_username" || -z "$git_email" ]] && die "Username and email are required"

    git config --global user.name "$git_username"
    git config --global user.email "$git_email"
    git config --global core.editor "vim"
    git config --global core.excludesfile "~/.gitignore"
    git config --global gpg.program "$(brew --prefix)/bin/gpg"
    git config --global commit.gpgsign "true"
    git config --global tag.gpgsign "true"
    git config --global init.defaultBranch "main"

    configure_gpg_key

    ok "Git configured: $git_username <$git_email>"
}

main() {
    read -rp "Configure git user settings? (y/n): " answer
    [[ "$answer" == "y" ]] && configure_git || true
}

main
