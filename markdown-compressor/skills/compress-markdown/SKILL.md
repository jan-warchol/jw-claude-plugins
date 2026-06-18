---
name: compress-markdown
description: Compress a markdown document (plan, spec, reference, or any prose-heavy doc) so it uses fewer words while keeping all of the information and roughly the same structure. Use when asked to shorten, tighten, condense, or reduce the word count of a markdown file without losing content.
---

Rewrite a markdown document into tighter prose so it uses **fewer words while keeping all the
information**. This is lossless compression of language, not of content.

## What "shorter" means here

The target metric is **alphanumeric words** (and, secondarily, alphanumeric characters): tokens that
contain at least one letter or digit. Measure it with the `count_words` MCP tool from this plugin,
not with `wc`.

- `wc -w` counts punctuation and markdown formatting (`###`, `1.`, `|---|`, `*`, `-`) as if they
  were words. They are not, and they must be preserved, so `wc` points you the wrong way.
- A bullet list of five items has fewer real words than the same items jammed into one sentence with
  commas and "and", even though `wc -w` may say the opposite. Prefer the structured form.

So: keep punctuation and markdown formatting free of cost, and judge progress only by `count_words`.

## Hard rules — do not break these

- **Do not touch whitespace to save size.** Blank lines, indentation, and line breaks are free.
  Never collapse paragraphs, remove blank lines, or reflow text to "save space".
- **Line count is irrelevant.** Do not try to reduce, balance, or optimize the number of lines.
  Use as many lines as readability wants.
- **Lose no information.** Every fact, constraint, number, name, edge case, caveat, and decision in
  the original must still be present and findable.
- **Preserve structure.** Keep YAML frontmatter verbatim. Keep the heading hierarchy, ordering, code
  blocks, tables, links, and identifiers. Convert prose to lists/tables *to clarify*, not to
  reorganize the document.

## Workflow

1. **Measure the baseline.** Call `count_words` on the file. Note `alphanumeric_words`.
2. **Read the whole document** so you understand what every part is saying before cutting.
3. **Rewrite in place** applying the techniques below, section by section.
4. **Measure again** with `count_words` and confirm the word count dropped.
5. **Verify nothing was lost:** re-read the new version against the old and check every fact,
   number, and requirement survived. If anything is gone, restore it.

## Compression techniques

Tightening prose (biggest wins):

- Cut filler and throat-clearing: "in order to" -> "to", "it is important to note that" -> drop,
  "due to the fact that" -> "because", "a number of" -> "several", "at this point in time" -> "now".
- Remove redundancy: words that restate the heading, the previous sentence, or an obvious implication.
- Prefer strong verbs over noun phrases: "make a decision about" -> "decide", "is responsible for
  handling" -> "handles".
- Drop hedging and meta-commentary that carries no information ("basically", "essentially", "as
  mentioned above") unless the cross-reference is load-bearing.
- Merge sentences that share a subject; delete sentences that only transition.

Restructuring prose into denser forms (keeps info, cuts words, *adds* clarity):

- Turn comma-enumerations into bullet lists ("supports A, B, C, and D" -> a 4-item list).
- Turn repeated "if X then Y" prose or attribute/value descriptions into a table.
- Pull a repeated phrase into a heading or list intro stated once instead of per item.
- Use markdown formatting freely — it does not count toward the word total.

What NOT to compress away:

- Specific numbers, thresholds, paths, names, IDs, versions, error strings.
- Conditions, exceptions, and "unless/except" clauses.
- Rationale that explains *why* a decision was made, when present.

## Counting tool

This plugin provides the `count_words` MCP tool. Call it with a file `path` (preferred — cheaper on
context than pasting `text`). It returns `alphanumeric_words` and `alphanumeric_characters`. The same
logic is available as a CLI fallback: `python3 <plugin>/scripts/wordcount_server.py <file.md>`.
