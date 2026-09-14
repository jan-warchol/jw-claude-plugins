#!/usr/bin/env bash
# Run both scripts on the examples and compare with the expected output.
# Expected values use --chars-per-word 1 (raw alphanumeric character counts),
# which makes them easy to verify by hand. Pass --update to regenerate them.
set -euo pipefail
cd "$(dirname "$0")/examples"
scripts=../../scripts
declare -A outputs=(
  [markdown.json]="$scripts/markdown-metrics.py --json --chars-per-word 1 markdown-basic.md"
  [mermaid.json]="$scripts/mermaid-metrics.py --json --chars-per-word 1 flowchart-edge-cases.mmd sequence.mmd class.mmd diagrams-in-markdown.md"
)
status=0
for name in "${!outputs[@]}"; do
  if [[ "${1:-}" == "--update" ]]; then
    ${outputs[$name]} > "../expected/$name"
  elif diff -u "../expected/$name" <(${outputs[$name]}); then
    echo "ok: $name"
  else
    echo "FAIL: $name"; status=1
  fi
done
exit $status
