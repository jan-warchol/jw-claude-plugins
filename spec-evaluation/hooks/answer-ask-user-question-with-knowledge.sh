#!/usr/bin/env bash
#
# PreToolUse hook for AskUserQuestion — "simulated user" for eval runs.
#
# If $CLAUDE_EVAL_SIM_USER_KNOWLEDGE_PATH points at a readable file, this hook
# answers every question in the AskUserQuestion payload by asking a headless
# `claude -p` to role-play a user who has extra knowledge from that file, then
# returns the answers via `updatedInput` so the tool resolves without prompting.
#
# Bails silently (prints nothing, exits 0 — the tool then prompts a real human)
# if: the env var is unset/empty; the file is missing/unreadable; `jq` or
# `claude` aren't on PATH; the payload isn't an AskUserQuestion call; or the
# simulated user's reply can't be parsed as a JSON object.
#
# Requires: jq, and the `claude` CLI on PATH with working auth.
# Optional:  $CLAUDE_EVAL_SIM_USER_MODEL  -> passed to `claude -p --model`.
#
#
# USAGE
#
# Setting the model is optional, but can optimize the cost and latency. There's no lever
# for effort now, but maybe we should add one.
#
# export CLAUDE_EVAL_SIM_USER_MODEL=claude-haiku-4-5
# export CLAUDE_EVAL_SIM_USER_MODEL=claude-sonnet-4-6
#
# Setting the knowledge path is required, otherwise the hook will disengage immediately.
#
# export CLAUDE_EVAL_SIM_USER_KNOWLEDGE_PATH=/knowledge/file/path
#
# Perhaps the most convenient option would be to just set it on the claude command line:
# CLAUDE_EVAL_SIM_USER_MODEL=claude-sonnet-4-6 CLAUDE_EVAL_SIM_USER_KNOWLEDGE_PATH=/knowledge/file/path claude
#

set -u

KNOWLEDGE_PATH="${CLAUDE_EVAL_SIM_USER_KNOWLEDGE_PATH:-}"
[[ -n "$KNOWLEDGE_PATH" && -f "$KNOWLEDGE_PATH" && -r "$KNOWLEDGE_PATH" ]] || exit 0
command -v jq     >/dev/null 2>&1 || exit 0
command -v claude >/dev/null 2>&1 || exit 0

INPUT="$(cat)"
[[ "$(jq -r '.tool_name // empty' <<<"$INPUT" 2>/dev/null)" == "AskUserQuestion" ]] || exit 0

TOOL_INPUT="$(jq -c '.tool_input' <<<"$INPUT" 2>/dev/null)"
[[ -n "$TOOL_INPUT" && "$TOOL_INPUT" != "null" ]] || exit 0
QUESTIONS="$(jq -c '.tool_input.questions // []' <<<"$INPUT" 2>/dev/null)"
[[ "$(jq 'length' <<<"$QUESTIONS" 2>/dev/null)" -gt 0 ]] || exit 0

KNOWLEDGE="$(cat "$KNOWLEDGE_PATH")"

PROMPT="$(cat <<EOF
You are simulating a human user clicking through an interactive multiple-choice
prompt inside a developer tool. Answer the way that user would.

Base your answers about the following knowledge. Don't stray from the knowledge and
never give answers contradicting it.
<<<KNOWLEDGE
${KNOWLEDGE}
KNOWLEDGE

These are the questions being asked, as JSON (the shape AskUserQuestion uses):
${QUESTIONS}

Rules:
- Answer EVERY question.
- Pick the option whose "label" the user would choose given their knowledge,
  and copy that label verbatim.
- If "multiSelect" is true you may pick several; join their labels with " || ".
- Never give answers contradicting the knowledge.
- Only if no listed option is acceptable, answer with free text instead.
    - If writing free text answer, tend to make it succinct and don't volunteer to provide extra information.
- If the answer is not clear from the knowledge and it's likely that an actual developer
  would be unsure of the correct answer, you are free to give answer like "unclear",
  "I don't know", "TBD", or even "I don't care".
- Output ONLY a JSON object mapping each question's exact "question" string to
  the chosen answer string. No commentary, no markdown fences.
EOF
)"

# Ask the simulated user. Run from an empty dir so the headless instance picks
# up no project context — it should know only what we put in the prompt above.
# (It still loads ~/.claude/ — user-level memory/settings. Add --settings etc.
# here if you want tighter isolation.)
MODEL_ARGS=()
[[ -n "${CLAUDE_EVAL_SIM_USER_MODEL:-}" ]] && MODEL_ARGS=(--model "$CLAUDE_EVAL_SIM_USER_MODEL")
WORKDIR="$(mktemp -d)"
RAW="$(cd "$WORKDIR" && printf '%s' "$PROMPT" | claude -p --bare --no-session-persistence --permission-mode dontAsk "${MODEL_ARGS[@]}" 2>/dev/null)"
rm -rf "$WORKDIR"

# Parse the reply as a JSON object; tolerate a stray ```json ... ``` fence.
ANSWERS="$(jq -ce 'if type == "object" then . else empty end' <<<"$RAW" 2>/dev/null)"
if [[ -z "$ANSWERS" ]]; then
  ANSWERS="$(sed -n '/```/,/```/p' <<<"$RAW" | sed '1d;$d' \
            | jq -ce 'if type == "object" then . else empty end' 2>/dev/null)"
fi
[[ -n "$ANSWERS" && "$(jq 'length' <<<"$ANSWERS" 2>/dev/null)" -gt 0 ]] || exit 0

# Emit the decision: pre-fill `answers` in the original tool input.
jq -nc \
  --argjson ti  "$TOOL_INPUT" \
  --argjson ans "$ANSWERS" \
  '{ hookSpecificOutput: {
       hookEventName: "PreToolUse",
       permissionDecision: "allow",
       updatedInput: ($ti + { answers: (($ti.answers // {}) + $ans) })
     } }'
