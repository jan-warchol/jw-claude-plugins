---
name: mermaid-metrics
description: Measure size of mermaid flowcharts, sequence diagrams and class diagrams. Use when you need to know how big or complex a diagram is.
---

Run `${CLAUDE_SKILL_DIR}/../../scripts/mermaid-metrics.py FILE...` on `.mmd` files or markdown files with mermaid blocks (add `--json` for JSON), or pipe a diagram or markdown to it on standard input.

A diagram's size is its `nodes`, `connections` and `normalized_words` (letters and digits of visible labels divided by 6). Judge them together, since a diagram can be hard to read because of many elements or long labels. Keywords, IDs behind labels and styling are not counted. Treat any `unparsed_lines` as uncounted.
