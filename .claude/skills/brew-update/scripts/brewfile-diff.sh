#!/bin/bash
# Compare installed Homebrew packages against the repo Brewfile.
# Usage: brewfile-diff.sh [path/to/Brewfile]
# Output: "type name" lines under ADD / REMOVE section markers.
# Compared types: tap, brew, cask, mas, uv.
# npm is excluded: `brew bundle dump` only sees `npm -g` and this machine
# installs globals via pnpm, so npm entries would always show as REMOVE.
# vscode/go/cargo are not managed in this Brewfile and are ignored.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BREWFILE="${1:-$SCRIPT_DIR/../../../../Brewfile}"

[[ -f "$BREWFILE" ]] || { echo "ERROR: Brewfile not found: $BREWFILE" >&2; exit 1; }

normalize() {
    awk '
        /^(tap|brew|cask|mas|uv)[[:space:]]/ {
            if (match($0, /"[^"]+"/)) {
                print $1 " " substr($0, RSTART + 1, RLENGTH - 2)
            }
        }' "$1" | sort -u
}

installed="$(mktemp)"
declared="$(mktemp)"
trap 'rm -f "$installed" "$declared"' EXIT

HOMEBREW_NO_AUTO_UPDATE=1 brew bundle dump --file=- | normalize /dev/stdin > "$installed"
normalize "$BREWFILE" > "$declared"

echo "== ADD (installed, not in Brewfile) =="
comm -23 "$installed" "$declared"
echo "== REMOVE (in Brewfile, not installed) =="
comm -13 "$installed" "$declared"
