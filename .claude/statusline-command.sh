#!/bin/bash
input=$(cat)

MODEL=$(echo "$input" | jq -r '.model.display_name // "Unknown"')
CURRENT_DIR=$(echo "$input" | jq -r '.workspace.current_dir // empty')
DIR_NAME="${CURRENT_DIR##*/}"

CONTEXT_SIZE=$(echo "$input" | jq -r '.context_window.context_window_size // 200000')
INPUT_TOKENS=$(echo "$input" | jq -r '.context_window.current_usage.input_tokens // 0')
CACHE_CREATE=$(echo "$input" | jq -r '.context_window.current_usage.cache_creation_input_tokens // 0')
CACHE_READ=$(echo "$input" | jq -r '.context_window.current_usage.cache_read_input_tokens // 0')
TOTAL_TOKENS=$((INPUT_TOKENS + CACHE_CREATE + CACHE_READ))
PERCENT=$((TOTAL_TOKENS * 100 / CONTEXT_SIZE))

echo "[$MODEL] $DIR_NAME | Context: ${PERCENT}%"
