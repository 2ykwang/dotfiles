#!/bin/bash
# Common functions for setup scripts

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging
info()    { printf "${BLUE}[INFO]${NC} %s\n" "$1"; }
ok()      { printf "${GREEN}[OK]${NC} %s\n" "$1"; }
warn()    { printf "${YELLOW}[WARN]${NC} %s\n" "$1"; }
err()     { printf "${RED}[ERROR]${NC} %s\n" "$1"; }
die()     { err "$1"; exit 1; }

# Get base directory (dotfiles root)
get_base_dir() {
    cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd
}
