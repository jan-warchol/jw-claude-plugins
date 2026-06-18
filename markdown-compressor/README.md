# markdown-compressor

Compress markdown documents — plans, specifications, references, any prose-heavy doc — into tighter
prose that uses **fewer words while keeping all the information and roughly the same structure**.

## What's inside

- **`compress-markdown` skill** — guidance for losslessly tightening a markdown document: cut filler,
  prefer dense structure (lists/tables) over comma-enumerations, and never touch whitespace or chase
  line count.
- **`markdown-wordcount` MCP server** — a `count_words` tool that reports two numbers for a file (or
  raw text):
  - `alphanumeric_words` — whitespace-delimited tokens containing at least one letter or digit
  - `alphanumeric_characters` — count of letter/digit characters

  Punctuation and markdown formatting (`###`, `1.`, `|---|`, `*`) are deliberately **not** counted,
  so this is the right metric for prose length — unlike `wc`, which counts symbols and formatting.

## Why not `wc`?

`wc -w` treats punctuation and markdown as words and rewards collapsing whitespace. That pushes you
toward worse documents. `count_words` measures only real words, so a 5-item bullet list correctly
scores lower than the same items crammed into one comma-laden sentence.

## Usage

Ask Claude to "compress" or "shorten" a markdown file; the skill drives the rewrite and uses the MCP
tool to measure before/after. The counter can also be run standalone:

```
python3 scripts/wordcount_server.py path/to/file.md
```

The script doubles as both the MCP stdio server (no arguments) and a plain CLI (with file
arguments), and depends only on the Python standard library.

The plugin bundles a `PreToolUse` hook (`hooks/`) that auto-approves the word counter — both the
`count_words` MCP tool and the `wordcount_server.py` CLI — so installing the plugin pre-approves it
and you are never prompted to run it.
