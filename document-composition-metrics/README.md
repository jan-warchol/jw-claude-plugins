# document-composition-metrics

Measure the size and structure of documents better than a word count. Markdown formatting and
punctuation are not counted, so shortening a document by these metrics never rewards removing
bullets, headings or tables.

Supported for now: markdown documents and mermaid flowcharts, sequence diagrams and class diagrams.

## Scripts

### `scripts/markdown-metrics.py`

```
scripts/markdown-metrics.py [--json] [--chars-per-word N] [FILE.md ...]
```

Requires [uv](https://docs.astral.sh/uv/). The `mistletoe` dependency is declared inline and
installed automatically. With no `FILE`, or with `-`, reads standard input.

| Metric                | Meaning                                                    |
|-----------------------|------------------------------------------------------------|
| `normalized_words`    | normalized words in the document (code included, front matter excluded) |
| `code_percent`        | % of non-whitespace characters in code blocks and inline code |
| `sections`            | number of sections (text between headings)                 |
| `section_words`       | section length                                             |
| `paragraph_words`     | paragraph length                                           |
| `list_words`          | length of a whole top-level list                           |
| `list_item_words`     | length of a list item's own text                           |

The last four are distributions, reported as the 15th, 50th and 85th percentile (`p15`, `p50`,
`p85`), or empty when the document has no such element.

### `scripts/mermaid-metrics.py`

```
scripts/mermaid-metrics.py [--json] [--chars-per-word N] [FILE ...]
```

Plain Python 3, no dependencies. Accepts `.mmd` files, or markdown files (each ` ```mermaid ` block
is measured separately). With no `FILE`, or with `-`, reads standard input, treated as markdown if
it contains a ` ```mermaid ` block and as a single diagram otherwise. Any lines it could not parse
are listed in `unparsed_lines`.

| Metric             | Flowchart | Sequence diagram                  | Class diagram   |
|--------------------|-----------|-----------------------------------|-----------------|
| `nodes`            | nodes     | participants                      | classes         |
| `connections`      | links     | messages                          | relationships   |
| `groups`           | subgraphs | boxes and blocks (`loop`, `alt`…) | namespaces      |
| `normalized_words` | normalized words of all visible text | | |

## Tests

`tests/run-tests.sh` runs both scripts on `tests/examples/` and compares the output with
`tests/expected/`. The expected values use `--chars-per-word 1`, so they are plain character
counts that can be checked by hand. `--update` regenerates them.

## Normalized words

```
normalized words = alphanumeric characters / 6
```

Markup, punctuation, whitespace, URLs and HTML are not counted. Contractions, short words,
numbers and timestamps count by their length instead of by how they happen to be split into
tokens. See [DESIGN.md](DESIGN.md) for the reasons and for exactly what each metric counts.
