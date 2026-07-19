# dotfiles

macOS dotfiles managed with GNU Stow and a Justfile.

## Install

```sh
git clone https://github.com/2ykwang/dotfiles ~/dotfiles
cd ~/dotfiles
bash scripts/brew.sh   # Homebrew + Brewfile packages (installs stow, just)
just link plugins configure
```

After the first setup, `just all` runs every step at once.

## Commands

| command | description |
| --- | --- |
| `just link` / `just unlink` | create/remove symlinks with stow |
| `just brew` | install Homebrew and Brewfile packages |
| `just plugins` | oh-my-zsh, zsh plugins, tmux (tpm) |
| `just configure` | interactive git user / GPG signing setup |

## Layout

Each top-level directory is a stow package mirroring `$HOME`:
`zsh`, `vim`, `tmux`, `git`, `ghostty`, `gnupg`, `lazygit`, `claude`.

- `claude/.claude/` — Claude Code global settings (`CLAUDE.md`, `settings.json`), linked into `~/.claude`
- `zsh/.config/zsh/aliases-secret.zsh` — machine-local secrets, untracked; `.zshrc` sources it only when present
- `.claude/skills/brew-update/` — project skill; run `/brew-update` in this repo to sync the Brewfile with installed packages

## Git / GPG

`just configure` sets git user, signing key and defaults.
GPG key setup: [GitHub guide](https://docs.github.com/en/authentication/managing-commit-signature-verification/generating-a-new-gpg-key)
