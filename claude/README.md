# Claude Code Configuration

Claude Code settings and custom commands managed via dotfiles.

## Structure

```
claude/
├── CLAUDE.md              # Global memory (personal preferences)
├── settings.json          # Claude Code settings
├── statusline-command.sh  # Statusline integration script
├── commands/              # Custom slash commands
│   ├── gh-issue.md        # /gh-issue - Analyze GitHub issues
│   ├── gh-pr.md           # /gh-pr - Analyze PRs with code review
│   └── gh-review.md       # /gh-review - Summarize PR reviews
└── README.md
```

## Setup

The `setup.sh` script creates symlinks from `~/.claude/` to this directory:

```bash
~/.claude/CLAUDE.md          → dotfiles/claude/CLAUDE.md
~/.claude/settings.json      → dotfiles/claude/settings.json
~/.claude/statusline-command.sh → dotfiles/claude/statusline-command.sh
~/.claude/commands/          → dotfiles/claude/commands/
```

## Custom Commands

| Command | Description |
|---------|-------------|
| `/gh-issue <number\|URL>` | Analyze and summarize a GitHub issue |
| `/gh-pr <number\|URL>` | Analyze a PR and provide code review |
| `/gh-review <number\|URL>` | Summarize review comments on a PR |

## Global Memory (CLAUDE.md)

Personal preferences applied to all projects:

- Response language
- Communication style
- Code review preferences
- Testing practices
