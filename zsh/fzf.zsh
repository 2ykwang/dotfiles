# =====================================
# fzf configuration
# =====================================

# fzf 기본 옵션
export FZF_DEFAULT_OPTS="
  --height=40%
  --layout=reverse
  --border=rounded
  --info=inline
  --preview-window=right:50%:wrap
"

# Ctrl+T: 파일 검색 (bat 프리뷰)
export FZF_CTRL_T_OPTS="
  --preview 'bat --style=numbers --color=always --line-range=:500 {} 2>/dev/null || cat {}'
"

# Alt+C: 디렉터리 이동 (tree 프리뷰)
export FZF_ALT_C_OPTS="
  --preview 'ls -la --color=always {} | head -50'
"

# fzf-tab: tab completion을 fzf로 대체
# 디렉터리 프리뷰 (ls)
zstyle ':fzf-tab:complete:cd:*' fzf-preview 'ls -la --color=always $realpath'
zstyle ':fzf-tab:complete:ls:*' fzf-preview 'ls -la --color=always $realpath 2>/dev/null || bat --style=numbers --color=always $realpath 2>/dev/null'

# 파일 프리뷰 (bat)
zstyle ':fzf-tab:complete:*:*' fzf-preview '
  if [[ -d $realpath ]]; then
    ls -la --color=always $realpath
  elif [[ -f $realpath ]]; then
    bat --style=numbers --color=always --line-range=:200 $realpath 2>/dev/null || cat $realpath
  fi
'

# fzf-tab 스타일
zstyle ':fzf-tab:*' fzf-flags --height=40% --layout=reverse --border=rounded
zstyle ':fzf-tab:*' switch-group ',' '.'  # 그룹 전환: , .

# fzf keybindings & completion 로드
[[ -f ~/.fzf.zsh ]] && source ~/.fzf.zsh

# Homebrew fzf 경로 (Apple Silicon / Intel)
if [[ -f /opt/homebrew/opt/fzf/shell/key-bindings.zsh ]]; then
  source /opt/homebrew/opt/fzf/shell/key-bindings.zsh
  source /opt/homebrew/opt/fzf/shell/completion.zsh
elif [[ -f /usr/local/opt/fzf/shell/key-bindings.zsh ]]; then
  source /usr/local/opt/fzf/shell/key-bindings.zsh
  source /usr/local/opt/fzf/shell/completion.zsh
fi
