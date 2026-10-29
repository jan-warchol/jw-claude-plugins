---
name: markdown-metrics
description: Measure size and structure of markdown documents. Use instead of `wc` whenever you need a document's length, e.g. to keep it within a word limit or compare versions.
---

Run `${CLAUDE_SKILL_DIR}/../../scripts/markdown-metrics.py FILE.md...` (add `--json` for JSON), or pipe markdown to it on standard input.

Use `normalized_words` as the document's size, not `wc -w`. It counts letters and digits divided by 6, so markdown syntax and punctuation cost nothing. Bullets, headings and tables are never worth removing just to shrink the count. Short words, contractions, URLs, numbers and timestamps count by their real length.

The other metrics are section, paragraph, list and list item lengths in the same unit, each given as the 15th, 50th and 85th percentile, plus `code_percent`.

`structured_percent` is the share of text in list items and table cells rather than paragraphs. Only the first 13 words of each item or cell count as structured, so long bullets count as prose. `anchor_gap_words` is the length of plain text between visual anchors (paragraph and item starts, headings, bold, italics, code, links). High p85 means walls of text. Very low values mean so much stands out that nothing does.
