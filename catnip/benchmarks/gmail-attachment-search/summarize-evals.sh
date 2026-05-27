#!/bin/bash

set -euo pipefail

USAGE="$(
cat <<EOF
Usage:

  $0 <outputs_dir (relative to benchmarks/gmail-attachment-search)> [... more directories]
EOF
)"

function die () {
  echo >&2 "$@"
  exit 2
}

function die_with_usage () {
  echo >&2 "ERROR: $*"
  echo >&2
  echo >&2 "$USAGE"
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


if (( $# < 1 )); then
  die_with_usage "No arguments given"
fi

PARENT_DIR="catnip/benchmarks/gmail-attachment-search"

OUTPUTS_DIRS=()
SUMMARY_NAME='results-summary'

while (( $# )); do
  OUTPUTS_DIR="$PARENT_DIR/$1"

  if ! [[ -d "$OUTPUTS_DIR" ]]; then
    die_with_usage "'$OUTPUTS_DIR' is not a directory"
  fi

  OUTPUTS_DIRS+=("$OUTPUTS_DIR")
  SUMMARY_NAME="$SUMMARY_NAME--$1"

  shift
done

SUMMARY_NAME="$SUMMARY_NAME.md"
SUMMARY_PATH="$PARENT_DIR/$SUMMARY_NAME"

if [[ -e "$SUMMARY_PATH" ]]; then
  die "'$SUMMARY_PATH' already exists"
fi

TOTALS_AND_SCORES="$(
  for OUTPUTS_DIR in "${OUTPUTS_DIRS[@]}"; do
    echo "Samples in $OUTPUTS_DIR"

    for SAMPLE_DIR in "$OUTPUTS_DIR/"*; do
      if ! [[ -d "$SAMPLE_DIR" ]]; then
          echo >&2 "WARN: $SAMPLE_DIR is not a subdirectory, skipping."
          continue
      fi

      echo "$SAMPLE_DIR"

      echo 'Structural eval totals:'
      for seval in "$SAMPLE_DIR/structural-eval"*".md"; do
        grep '| \*\*Total' <"$seval" | tail -n1
      done

      echo 'Tech eval score'
      grep '| \*\*Score' <"$SAMPLE_DIR/tech-eval.md"

      echo
    done
  done
)"

echo "Raw results extracted from the evals:

$TOTALS_AND_SCORES

"

echo "Formatting the results into a table with claude..."

claude --model claude-sonnet-4-6 --effort medium -p "Hey, I extracted some results from evaluations and would like to put them in a nice table. The repeated totals
are separate runs of the same eval job - there is some randomness involved. Please just put them in a single
cell and separate by a comma. I'd mostly like to compare the top-level directories (printed in 'Samples in X' lines).
Please provide 3 tables:

a) a table of top-level directories where only avg/min/max values are visible for each of these directories. Group columns by the eval type first.
b) same as a), but group he columns by avg/min/max first.
c) more detailed breakdown with all the individual results.

Label tables with ## headers, drop the a), b), c).

The data is as follows:

$TOTALS_AND_SCORES
" \
  | tee_md "$SUMMARY_PATH"

echo "Markdown copy stored to $SUMMARY_PATH"
