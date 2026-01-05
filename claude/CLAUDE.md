- Respond in Korean
- Before implementing, ask clarifying questions if requirements are ambiguous or incomplete
- Be skeptical: challenge assumptions, identify potential issues, and point out edge cases rather than assuming things will work
- When fixing bugs, write a failing regression test first before implementing the fix

## Dotfiles Configuration Guidelines

When adding new environments or settings, follow these rules:

1. **Brewfile**: New packages must be added to Brewfile with explanatory comments
2. **Config files**: Create related config files in appropriate folders within the dotfiles repo (e.g., `gnupg/`, `git/`, `zsh/`)
3. **setup.sh integration**: Add symbolic links for new config files to the links array in the `link_dotfiles()` function
4. **Directory creation**: Add required directories to the "Ensure directories exist" section in setup.sh
5. **Permissions**: Handle special permissions (e.g., `.gnupg` requires 700) in setup.sh