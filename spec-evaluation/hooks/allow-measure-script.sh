#!/usr/bin/env bash
# PreToolUse hook — auto-approve uv run measure.py invocations.

INPUT="$(cat)"
[[ "$(jq -r '.tool_name // empty' <<<"$INPUT" 2>/dev/null)" == "Bash" ]] || exit 0

COMMAND="$(jq -r '.tool_input.command // empty' <<<"$INPUT" 2>/dev/null)"
[[ "$COMMAND" == *"measure.py"* ]] || exit 0

printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}'
