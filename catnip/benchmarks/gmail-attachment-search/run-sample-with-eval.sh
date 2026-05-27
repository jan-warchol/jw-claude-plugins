#!/bin/bash

set -euo pipefail

function die () {
  echo >&2 "$@"
  exit 2
}

function assert_command_available () {
  command -v "$1" >/dev/null 2>&1 || die "$1 command is missing."
}

assert_command_available claude
assert_command_available pandoc


function format_md () {
  pandoc -r commonmark_x -w ansi
}

function echo_md () {
  echo "$@" | format_md
}

function tee_md () {
  tee "$@" | format_md
}

MODEL=claude-sonnet-4-6
EFFORT=high

CLAUDE="claude --model $MODEL --effort $EFFORT"

PROMPT='Create a simple Python script that searches Gmail for emails matching a user-provided query, then returns the last 3 matching emails that have attachments.'
TECH_EVAL_CRITERIA_PATH=catnip/benchmarks/gmail-attachment-search/tech-criteria.md

OUTPUTS_DIR="${1:-catnip/benchmarks/gmail-attachment-search/catnip-phased--tasks}"

mkdir -p "$OUTPUTS_DIR"


EXEC_LOG=iterative-spec-writing.log.md

echo "## Running iterative-spec-writing" | format_md
echo

$CLAUDE --plugin-dir ./catnip -p "/catnip:iterative-spec-writing $PROMPT" \
  | tee_md "$EXEC_LOG"

PROCESS_DIR=$(grep 'Process directory' "$EXEC_LOG" | tail -n1 | sed -E 's/^.*: `?([^`]+)`?.*$/\1/')
FINAL_PATH=$(grep 'Spec file' "$EXEC_LOG" | tail -n1 | sed -E 's/^.*: `?([^`]+)`?.*$/\1/')

format_md <<EOF

## Spec is ready.

**Process directory**: $PROCESS_DIR
**Final spec path**: $FINAL_PATH

EOF

if ! [[ -d "$PROCESS_DIR" ]]; then
  die "ERROR: '$PROCESS_DIR' is not a directory"
fi

if ! [[ -f "$FINAL_PATH" ]]; then
  die "ERROR: '$FINAL_PATH' is not a file"
fi

if ! diff -q "$PROCESS_DIR/compressed.md" "$FINAL_PATH"; then
  >&2 echo "Final spec is not the same as compressed.md."
  exit 1
fi

echo_md "_Verified that final spec is identical to compressed.md, removing the final spec copy._"

rm "$FINAL_PATH"

EVAL_NUM=0
OUTPUT_DIR=""

while [[ -z "$OUTPUT_DIR" ]] || [[ -e "$OUTPUT_DIR" ]]; do
  ((++EVAL_NUM))
  OUTPUT_DIR="$(printf '%s/%02d' "$OUTPUTS_DIR" "$EVAL_NUM")"
done

echo_md "_Copying the process dir to \`$OUTPUT_DIR\`_"

cp -r "$PROCESS_DIR" "$OUTPUT_DIR"

mv "$EXEC_LOG" "$OUTPUT_DIR/"

# Run evals

format_md <<EOF

## Structural evaluation

EOF

$CLAUDE --plugin-dir ./spec-evaluation \
 -p "/spec-evaluation:structural-evaluation $OUTPUT_DIR/compressed.md" \
 | tee_md "$OUTPUT_DIR/structural-eval.md"

for i in 2 3; do
  echo_md "_Repeated structural evaluation (structural-eval-${i})_"

  $CLAUDE --plugin-dir ./spec-evaluation \
    -p "/spec-evaluation:structural-evaluation $OUTPUT_DIR/compressed.md" \
    | tee_md "$OUTPUT_DIR/structural-eval-$i.md"
done

format_md <<EOF

## Technical criteria evaluation

EOF

$CLAUDE --plugin-dir ./spec-evaluation \
  -p "/spec-evaluation:technical-evaluation spec: $OUTPUT_DIR/compressed.md criteria: $TECH_EVAL_CRITERIA_PATH" \
  | tee_md "$OUTPUT_DIR/tech-eval.md"

format_md <<EOF

## Evaluation done

**Output directory**: $OUTPUT_DIR

EOF
