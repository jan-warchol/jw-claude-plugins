---
name: markdown-metrics
description: Measure size and structure of markdown documents. Use instead of `wc` whenever you need a document's length, e.g. to keep it within a word limit or compare versions.
---

Run `${CLAUDE_SKILL_DIR}/../../scripts/markdown-metrics.py FILE.md...` (add `--json` for JSON).

Use `normalized_words` as the document's size, not `wc -w`. It counts letters and digits divided by 6, so markdown syntax and punctuation cost nothing. Bullets, headings and tables are never worth removing just to shrink the count. Short words, contractions, URLs, numbers and timestamps count by their real length.

The other metrics are averages in the same unit (section, paragraph, list, list item lengths), plus `code_percent`.
