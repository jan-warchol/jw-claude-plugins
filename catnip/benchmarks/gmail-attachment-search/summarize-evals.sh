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

assert_command_available python3
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

if (( ${#SUMMARY_NAME} > 100 )); then
  SUMMARY_NAME_MD5="$(md5sum <<<"$SUMMARY_NAME")"
  SUMMARY_NAME="${SUMMARY_NAME:0:87}---${SUMMARY_NAME_MD5:0:10}"
fi

SUMMARY_NAME="$SUMMARY_NAME.md"
SUMMARY_PATH="$PARENT_DIR/$SUMMARY_NAME"

if [[ -e "$SUMMARY_PATH" ]]; then
  die "'$SUMMARY_PATH' already exists"
fi

python3 "$PARENT_DIR/summarize-evals.py" "${OUTPUTS_DIRS[@]}" \
  | tee_md "$SUMMARY_PATH"

echo "Markdown copy stored to $SUMMARY_PATH"
