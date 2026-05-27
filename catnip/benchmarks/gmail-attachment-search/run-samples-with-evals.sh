#!/bin/bash

set -euo pipefail

USAGE="$(
cat <<EOF
Usage:

  $0 <outputs_dir (relative to benchmarks/gmail-attachment-search)> <number of samples to run>
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

if (( $# != 2 )); then
  die_with_usage "Wrong number of arguments ($#)."
fi

OUTPUTS_DIR="catnip/benchmarks/gmail-attachment-search/$1"

NUMBER_OF_SAMPLES_TO_RUN="$2"

if [[ -z "$1" ]] || [[ -e "$OUTPUTS_DIR" ]] && ! [[ -d "$OUTPUTS_DIR" ]]; then
  die_with_usage "'$OUTPUTS_DIR' is not a directory"
fi

if ! [[ "$NUMBER_OF_SAMPLES_TO_RUN" =~ ^[0-9]+$ ]] || (( NUMBER_OF_SAMPLES_TO_RUN < 1 )) || (( NUMBER_OF_SAMPLES_TO_RUN > 20 )); then
  die_with_usage "'$NUMBER_OF_SAMPLES_TO_RUN' is not a correct number of samples to run. Must be a number between 1 and 20."
fi

echo >&2 "Running $NUMBER_OF_SAMPLES_TO_RUN samples in $OUTPUTS_DIR..."

for (( i = 0; i < NUMBER_OF_SAMPLES_TO_RUN; ++i )); do
  ./run-sample-with-eval.sh "$OUTPUTS_DIR"
done
