---
name: compress-markdown
description: Compress a markdown document (plan, spec, reference, or any prose-heavy doc) so it uses fewer words while keeping all of the information and roughly the same structure. Use when asked to shorten, tighten, condense, or reduce the word count of a markdown file without losing content.
---

Rewrite a markdown document into tighter prose so it uses **fewer words while keeping all the
information**. This is lossless compression of language, not of content. You already know how to
tighten prose; this skill is about the non-obvious rules and the right metric.

## The metric

Judge length only by the `count_words` MCP tool from this plugin (it reports `alphanumeric_words` and
`alphanumeric_characters`). Do **not** use `wc`: it counts punctuation and markdown (`###`, `1.`,
`|---|`, `*`, `-`) as words, so it rewards the wrong changes. Real words are what you cut.

A consequence worth exploiting: formatting is free. A 5-item bullet list scores lower than the same
items in one comma-and-"and" sentence, so prefer lists and tables over enumerated prose — they cut
the count *and* read better.

## Hard rules

- **Never alter whitespace to save size**, and **ignore line count entirely** — both are free and
  irrelevant. Do not collapse blank lines, reflow paragraphs, or balance line lengths.
- **Match the original's line-wrapping**: if the source hard-wraps prose at a fixed width, wrap the
  rewrite at that same width; if the source leaves paragraphs on single unwrapped lines, keep it that
  way — never introduce wrapping as part of compression.
- **Lose no information**: every fact, number, name, path, condition, exception, caveat, and
  rationale must survive and stay findable.
- **Preserve structure**: keep YAML frontmatter verbatim; keep heading hierarchy, ordering, code
  blocks, tables, and links. Convert prose to lists/tables to clarify, not to reorganize.

## Workflow

1. `count_words` on the file to get a baseline.
2. Read it fully, then rewrite in place.
3. `count_words` again and confirm the count dropped.
4. Re-read old vs. new to confirm no fact was lost; restore anything missing.

The counter also runs standalone: `python3 <plugin>/scripts/wordcount_server.py <file.md>`.
