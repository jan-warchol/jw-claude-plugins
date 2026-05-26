#!/usr/bin/env bash
# PreToolUse hook — auto-approve Write and Bash operations related to .catnip/.

INPUT="$(cat)"
TOOL="$(jq -r '.tool_name // empty' <<<"$INPUT" 2>/dev/null)"

if [[ "$TOOL" == "Write" ]]; then
    FILE="$(jq -r '.tool_input.file_path // empty' <<<"$INPUT" 2>/dev/null)"
    [[ "$FILE" == *".catnip/"* ]] || exit 0
    printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}'

elif [[ "$TOOL" == "Bash" ]]; then
    CMD="$(jq -r '.tool_input.command // empty' <<<"$INPUT" 2>/dev/null)"
    # Allow mkdir for the .catnip directory structure
    if [[ "$CMD" == *"mkdir"* && "$CMD" == *".catnip"* ]]; then
        printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}'
    # Allow copying files to/from .catnip
    elif [[ "$CMD" == *"cp"* && "$CMD" == *".catnip/"* ]]; then
        printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}'
    # Allow python3 one-liners (e.g. word count) operating on .catnip/ files
    elif [[ "$CMD" == *"python3"* && "$CMD" == *".catnip/"* ]]; then
        printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}'
    fi
fi
