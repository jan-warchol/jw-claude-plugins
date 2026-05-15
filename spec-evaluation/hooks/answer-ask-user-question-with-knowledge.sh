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
# Setting the model and effort is optional, but can optimize the cost and latency. There's no lever
# for effort now, but maybe we should add one.
#
# export CLAUDE_EVAL_SIM_USER_MODEL=claude-haiku-4-5
# export CLAUDE_EVAL_SIM_USER_MODEL=claude-sonnet-4-6
#
# export CLAUDE_EVAL_SIM_USER_EFFORT=medium
#
# Setting the knowledge path is required, otherwise the hook will disengage immediately.
#
# export CLAUDE_EVAL_SIM_USER_KNOWLEDGE_PATH=/knowledge/file/path
#
# Perhaps the most convenient option would be to just set it on the claude command line:
# CLAUDE_EVAL_SIM_USER_MODEL=claude-sonnet-4-6 CLAUDE_EVAL_SIM_USER_EFFORT=medium CLAUDE_EVAL_SIM_USER_KNOWLEDGE_PATH=/knowledge/file/path claude
#

set -u

KNOWLEDGE_PATH="${CLAUDE_EVAL_SIM_USER_KNOWLEDGE_PATH:-}"
[[ -n "$KNOWLEDGE_PATH" && -f "$KNOWLEDGE_PATH" && -r "$KNOWLEDGE_PATH" ]] || exit 0

INPUT="$(cat)"
[[ "$(jq -r '.tool_name // empty' <<<"$INPUT" 2>/dev/null)" == "AskUserQuestion" ]] || exit 0

if ! command -v jq     >/dev/null 2>&1; then
  echo >&2 "'jq' command is missing, can't execute the hook."
  exit 2
fi
if ! command -v claude >/dev/null 2>&1; then
  echo >&2 "'claude' command is missing, can't execute the hook."
  exit 2
fi

# Bootstrap auth for `claude --bare`: if no API key is in env, lift the OAuth
# access token from the user's credentials file. The subprocess runs with
# `--bare`, which refuses OAuth/keychain reads and only honors ANTHROPIC_API_KEY
# (or apiKeyHelper via --settings). The `sk-ant-oat01-...` access token works
# when passed via ANTHROPIC_API_KEY, and bills against the user's subscription.
# Skipped if expired so the subprocess fails loudly rather than swallowing a 401.
if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
  CRED_FILE="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.credentials.json"
  if [[ -r "$CRED_FILE" ]]; then
    OAUTH_TOK="$(jq -r '.claudeAiOauth.accessToken // empty' "$CRED_FILE" 2>/dev/null)"
    OAUTH_EXP="$(jq -r '.claudeAiOauth.expiresAt // 0'     "$CRED_FILE" 2>/dev/null)"
    if [[ -n "$OAUTH_TOK" && "$OAUTH_EXP" -gt "$(($(date +%s) * 1000))" ]]; then
      export ANTHROPIC_API_KEY="$OAUTH_TOK"
    fi
  fi
fi

if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
  echo >&2 "ANTHROPIC_API_KEY is unset or empty and an attempt to get valid OAuth access token from .credentials.json failed. Can't use claude --bare."
  exit 2
fi

LOGFILE="$PWD/.answer-ask-user-question-with-knowledge.log.jsonl"
STDERR_LOG="$PWD/.answer-ask-user-question-with-knowledge.stderr.log"

jq -c '{ request: . }' <<<"$INPUT" >>"$LOGFILE"

TOOL_INPUT="$(jq -c '.tool_input' <<<"$INPUT" 2>/dev/null)"
if ! [[ -n "$TOOL_INPUT" && "$TOOL_INPUT" != "null" ]]; then
  echo >&2 "Empty .tool_input in request."
  exit 2
fi
QUESTIONS="$(jq -c '.tool_input.questions // []' <<<"$INPUT" 2>/dev/null)"
if ! [[ "$(jq 'length' <<<"$QUESTIONS" 2>/dev/null)" -gt 0 ]]; then
  echo >&2 "Empty .questions in request."
  exit 2
fi

(
  set -u
  set -e

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
  [[ -n "${CLAUDE_EVAL_SIM_USER_MODEL:-}" ]] && MODEL_ARGS+=(--model "$CLAUDE_EVAL_SIM_USER_MODEL")
  [[ -n "${CLAUDE_EVAL_SIM_USER_EFFORT:-}" ]] && MODEL_ARGS+=(--effort "$CLAUDE_EVAL_SIM_USER_EFFORT")

  WORKDIR="$(mktemp -d)"
  RAW="$(cd "$WORKDIR" && printf '%s' "$PROMPT" | claude -p --bare --tools '' --no-session-persistence --permission-mode dontAsk "${MODEL_ARGS[@]}")"
  CLAUDE_ERROR_CODE=$?
  rm -rf "$WORKDIR"

  # Parse the reply as a JSON object; tolerate a stray ```json ... ``` fence.
  ANSWERS="$(jq -ce 'if type == "object" then . else empty end' <<<"$RAW" 2>/dev/null)"
  if [[ -z "$ANSWERS" ]]; then
    ANSWERS="$(sed -n '/```/,/```/p' <<<"$RAW" | sed '1d;$d' \
              | jq -ce 'if type == "object" then . else empty end' 2>/dev/null)"
  fi
  if [[ -z "$ANSWERS" || "$(jq 'length' <<<"$ANSWERS" 2>/dev/null)" -le 0 ]]; then
    # We've committed to handling this AskUserQuestion (knowledge file present,
    # tools available, payload was a valid AskUserQuestion call) but the sim-user
    # subprocess failed to produce a usable JSON answer. Block the tool via
    # exit 2 and surface the cause — better than silently falling back to a
    # human prompt, which is what made this hook hard to debug previously.
    echo >&2 "Claude invocation failed to answer AskUserQuestion: output is empty or could not be parsed. claude exit code: $CLAUDE_ERROR_CODE"
    jq -R --slurp -c '{ rawClaudeOutput: . }' <<<"$RAW" >>"$LOGFILE"
    exit 2
  fi

  # Emit the decision: pre-fill `answers` in the original tool input.
  OUTPUT="$(
    jq -nc \
      --argjson ti  "$TOOL_INPUT" \
      --argjson ans "$ANSWERS" \
      '{ hookSpecificOutput: {
          hookEventName: "PreToolUse",
          permissionDecision: "allow",
          updatedInput: ($ti + { answers: (($ti.answers // {}) + $ans) })
        } }'
  )"

  jq -c '{ response: . }' <<<"$OUTPUT" >>"$LOGFILE"

  printf "%s" "$OUTPUT"

) 2>"$STDERR_LOG"

EXIT_CODE=$?

if ((EXIT_CODE)); then
  jq -c -R --slurp "{ exitCode: $EXIT_CODE, stderr: . }" <"$STDERR_LOG" >>"$LOGFILE"
  # Regardless of original error code, if there was an error, make it surface to the user.
  printf >&2 'Hook failed to answer the question.\nFull stderr: %s\nLog: %s\nLast lines of stderr:\n%s' "$STDERR_LOG" "$LOGFILE" "$(tail -n5 "$STDERR_LOG")"
  exit 2
fi
