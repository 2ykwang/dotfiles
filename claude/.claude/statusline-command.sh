#!/bin/bash
input=$(cat)

# Extract JSON data
CURRENT_DIR=$(echo "$input" | jq -r '.workspace.current_dir // empty')
MODEL_ID=$(echo "$input" | jq -r '.model.id // empty')

# Calculate context percentage
CONTEXT_SIZE=$(echo "$input" | jq -r '.context_window.context_window_size // 200000')
INPUT_TOKENS=$(echo "$input" | jq -r '.context_window.current_usage.input_tokens // 0')
CACHE_CREATE=$(echo "$input" | jq -r '.context_window.current_usage.cache_creation_input_tokens // 0')
CACHE_READ=$(echo "$input" | jq -r '.context_window.current_usage.cache_read_input_tokens // 0')
TOTAL_TOKENS=$((INPUT_TOKENS + CACHE_CREATE + CACHE_READ))
PERCENT=$((TOTAL_TOKENS * 100 / CONTEXT_SIZE))

# Extract model name with version (e.g., "Opus 4.5", "Sonnet 3.5")
MODEL_NAME=""
if [[ "$MODEL_ID" =~ claude-opus-([0-9])-([0-9]+) ]]; then
    MODEL_NAME="Opus ${BASH_REMATCH[1]}.${BASH_REMATCH[2]}"
elif [[ "$MODEL_ID" =~ claude-sonnet-([0-9])-([0-9]+) ]]; then
    MODEL_NAME="Sonnet ${BASH_REMATCH[1]}.${BASH_REMATCH[2]}"
elif [[ "$MODEL_ID" =~ claude-haiku-([0-9])-([0-9]+) ]]; then
    MODEL_NAME="Haiku ${BASH_REMATCH[1]}.${BASH_REMATCH[2]}"
elif [[ "$MODEL_ID" =~ opus ]]; then
    MODEL_NAME="Opus"
elif [[ "$MODEL_ID" =~ sonnet ]]; then
    MODEL_NAME="Sonnet"
elif [[ "$MODEL_ID" =~ haiku ]]; then
    MODEL_NAME="Haiku"
fi

# Convert absolute path to use ~ for home directory
DISPLAY_PATH="$CURRENT_DIR"
if [[ "$CURRENT_DIR" == "$HOME"* ]]; then
    DISPLAY_PATH="~${CURRENT_DIR#$HOME}"
fi

# Truncate path if too long (max 50 chars for absolute paths)
if [[ ${#DISPLAY_PATH} -gt 50 ]]; then
    DISPLAY_PATH="...${DISPLAY_PATH: -47}"
fi

# Get git info if in a git repository (skip optional locks for performance)
GIT_INFO=""
if git -C "$CURRENT_DIR" rev-parse --git-dir >/dev/null 2>&1; then
    BRANCH=$(git -C "$CURRENT_DIR" --no-optional-locks rev-parse --abbrev-ref HEAD 2>/dev/null)

    # Check for changes
    UNSTAGED=""
    STAGED=""
    if ! git -C "$CURRENT_DIR" --no-optional-locks diff --quiet 2>/dev/null; then
        UNSTAGED="!"
    fi
    if ! git -C "$CURRENT_DIR" --no-optional-locks diff --cached --quiet 2>/dev/null; then
        STAGED="+"
    fi

    if [[ -n "$BRANCH" ]]; then
        GIT_INFO=" [git/$BRANCH$UNSTAGED$STAGED]"
    fi
fi

# Color codes (using ANSI, will be dimmed in status line)
GREEN='\033[38;5;71m'
RESET='\033[0m'

# Output: model name, colored path with git info and context percentage
MODEL_PREFIX=""
if [[ -n "$MODEL_NAME" ]]; then
    MODEL_PREFIX="${MODEL_NAME} | "
fi

printf "${MODEL_PREFIX}${GREEN}${DISPLAY_PATH}${RESET}${GIT_INFO} | Context: ${PERCENT}%%"
