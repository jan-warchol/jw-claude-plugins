# Design: document size and structure metrics

## Goal

Give agents a measure of document size that reflects how much content a reader has to take in.
Agents act on the metric they get. A bad metric makes them optimize the wrong thing.

## The problem with word counts

`wc -w` counts whitespace-separated tokens. In markdown many of those tokens are not content:

| Source text                 | Tokens counted by `wc -w` | Actual content      |
|-----------------------------|---------------------------|---------------------|
| `- item`                    | 2 (`-`, `item`)           | 1 word              |
| `### Heading`               | 2                         | 1 word              |
| `\| a \| b \|`              | 5                         | 2 words             |
| `**Note:** text`            | 2                         | 2 words             |
| `https://some-website.com/some/path` | 1                | 6 words             |

An agent asked to shorten a document gets the best `wc` improvement by removing bullets, headings
and tables and packing the content into dense paragraphs. That makes the document harder to read,
harder to navigate, and less reliable to follow. A size metric must not penalize structure.

Filtering tokens ("count only tokens that contain a letter or digit") removes the markup, but other
distortions remain:

- **Contractions and possessives.** Replacing punctuation with spaces turns `it's` into two words.
  Keeping punctuation inside tokens makes `and/or` or `input/output` one word.
- **Short function words.** `a`, `of`, `to`, `in` each count as a full word, although they carry
  little information. One could argue they should not count at all.
- **Numbers.** Numbers are content and must count. But how much they count depends on arbitrary
  tokenization: `12` is one word, `1 000 000` is three.
- **Dates, times, identifiers.** `2026-09-14T10:30:00Z` becomes six words once punctuation is
  replaced by spaces, or one word if it is not. A reader processes it as about two units: a date
  and a time.

## Normalized word count

```
normalized words = alphanumeric characters / CHARS_PER_WORD
```

Count every letter and digit (Unicode-aware, so non-English text works), ignore everything else,
and divide by a constant typical word length. Default `CHARS_PER_WORD` is **6**.

What this solves:

- Markup and punctuation have no effect, so structure costs nothing. A bullet list scores the
  same as the same text written as a sentence with commas.
- Nothing depends on tokenization: `it's` = 3 characters ≈ 0.5 words, whether or not you
  split it.
- Short words weigh little: `a` is 1/6 of a word, `implementation` is more than two.
- Numbers and identifiers count by length: `12` ≈ 0.3 words, and the ISO timestamp above has
  16 alphanumeric characters ≈ 2.7 words. That is close to how much a reader takes in.

### Choosing the constant

Real words in this repository's markdown (code blocks excluded) average **~4.9 alphanumeric
characters**. With a constant of 6, a normalized count is about 80% of a conventional word count.
The discount comes mostly from short function words. That fits the intent: the metric measures
content, not tokens. A constant of 7 would give about 70%.

The absolute value matters less than consistency. Size limits and comparisons must use the same
constant. The scripts accept `--chars-per-word` for experiments. Keep the default for anything that
gets compared over time.

Known limitations: code identifiers are long (`get_user_by_id` ≈ 2 words) and scripts without
spaces (e.g. Chinese) have very different character density. Both are acceptable for the intended
use: English prose-heavy specs, plans and references.

## Markdown metrics

The document is parsed with [mistletoe](https://github.com/miyuki-ts/mistletoe). Characters come
from the parsed text rather than the raw source, so:

- **Counted:** visible text, including headings, table cells, link text, image alt text, inline
  code and code blocks.
- **Not counted:** link and image URLs, link reference definitions, HTML tags and comments, and
  front matter. None of these are read as prose.
- **Code** is part of `normalized_words`. `code_percent` tells how code-heavy the document is,
  regardless of its size. It counts non-whitespace characters, not only alphanumeric ones,
  because symbols (`()`, `{}`, `=`, `->`) are a real part of code. The denominator is the
  non-whitespace text of the parsed document, so markdown syntax (`#`, `|---|`, list markers)
  does not dilute the percentage. Mermaid blocks inside markdown count as code. Use `mermaid-metrics.py` to measure them
  properly.

Structure metrics use the same unit, and code blocks are excluded from them:

| Metric                | Unit measured                                                        |
|-----------------------|----------------------------------------------------------------------|
| `avg_section_words`   | body between two headings (text before the first heading is a section) |
| `avg_paragraph_words` | a paragraph, including in block quotes; list item text is not a paragraph |
| `avg_list_words`      | a whole top-level list, nested lists included                        |
| `avg_list_item_words` | one item's own text, nested sub-lists excluded                       |

Long average paragraphs point to walls of text. Long list items point to bullets that should be
paragraphs or split. Very short sections point to over-fragmentation.

## Mermaid metrics

The size of a diagram is not just its text. Every node and every connection is something the
reader has to find and hold in mind. So the size is measured on independent axes:

| Metric             | Flowchart                | Sequence diagram                                   | Class diagram |
|--------------------|--------------------------|----------------------------------------------------|---------------|
| `nodes`            | distinct nodes           | participants and actors, declared or implicit      | classes, declared or implicit |
| `connections`      | links                    | messages                                           | relationships |
| `groups`           | subgraphs                | boxes and blocks: `loop`, `alt`, `opt`, `par`, `critical`, `break`, `rect` | namespaces |

In a flowchart `A & B --> C & D` expands to 4 links, and a chain `A --> B --> C` is 2. `else`,
`and` and `option` are sections of a block, not new groups.

`normalized_words` counts the text the reader sees: node and participant labels, link and message
text, notes, block and subgraph titles, class members and annotations, relationship labels and
cardinalities, and the diagram title. An element without a label shows its ID, so the ID counts.
For an element with a label only the label counts. Keywords, arrows, style classes and style
definitions do not count.

Stripping punctuation from the whole diagram would get close to this. But it would also count
IDs next to their labels, `classDef`/`style` lines and keywords like `participant`, which can be
a large share of a small diagram. So diagrams are parsed.

### Parsing

Mermaid has no grammar that is easy to reuse from Python: the official parsers are JavaScript,
separate for each diagram type. The three supported types are small enough for hand-written
parsers:

- **Flowchart:** a scanner over the whole body, because quoted labels may span lines and
  statements may be separated by `;`. It supports node shapes, quoted labels,
  `@{ label: ... }`, `:::class`, `&` groups, chains, all link styles with `|label|` or
  `-- text -->` labels, and subgraphs.
- **Sequence and class diagrams:** line by line, one pattern per statement kind.

Lines a parser does not understand are listed in `unparsed_lines` instead of being guessed.
A result without that field was fully parsed.

Known gaps: a named box color (`box Aqua Title`) is counted as a word. CSS colors like
`rgb(...)` and `#hex` are not.

Other diagram types (state, ER, gantt, ...) are not parsed. For them only an approximate
`normalized_words` (all alphanumeric characters except header and comments) is reported. Each
new type needs its own definition of "node" and "connection".

### Open questions

- should we skip URLs or count them in any special way?
