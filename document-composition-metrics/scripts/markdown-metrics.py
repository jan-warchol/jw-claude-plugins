#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mistletoe>=1.3"]
# ///
"""Measure size and structure of markdown documents.

All lengths are in normalized words: alphanumeric characters / CHARS_PER_WORD.
Markdown syntax, punctuation, link targets, HTML and whitespace are not counted.
See DESIGN.md for the rationale.

Metrics per file:
  normalized_words      normalized words in the rendered text (code included;
                        front matter excluded)
  code_percent          % of non-whitespace characters of the rendered text that are
                        in code blocks or inline code
  avg_section_words     mean body words per section (content between headings)
  avg_paragraph_words   mean words per paragraph (list items excluded)
  avg_list_words        mean words per top-level list, nested lists included
  avg_list_item_words   mean words of an item's own text, nested lists excluded

Usage:
  markdown-metrics.py [--json] [--chars-per-word N] [FILE.md ...]

With no FILE, or when FILE is -, read standard input.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from mistletoe import Document
from mistletoe.html_renderer import HtmlRenderer

CHARS_PER_WORD = 6

FRONT_MATTER = re.compile(r"\A(---|\+\+\+)[ \t]*\r?\n.*?^\1[ \t]*(\r?\n|\Z)", re.DOTALL | re.MULTILINE)

CODE_TOKENS = ("CodeFence", "BlockCode", "InlineCode")
SKIPPED_TOKENS = ("HtmlBlock", "HtmlSpan")
BLOCK_CODE_TOKENS = ("CodeFence", "BlockCode")


# ── Character counting ───────────────────────────────────────────────────────

def alnum_chars(text):
    return sum(1 for c in text if c.isalnum())


def non_space_chars(text):
    return sum(1 for c in text if not c.isspace())


def _children(node):
    children = list(getattr(node, "children", None) or [])
    if type(node).__name__ == "Table" and node.header is not None:
        children.insert(0, node.header)
    return children


def count_chars(node, include_block_code=True, counter=alnum_chars):
    """Chars of a node's visible text, alphanumeric by default.

    Link and image targets are node attributes, not children, so only link text
    and alt text are counted. HTML is skipped.
    """
    name = type(node).__name__
    if name in SKIPPED_TOKENS:
        return 0
    if name in BLOCK_CODE_TOKENS and not include_block_code:
        return 0
    if name == "RawText":
        return counter(node.content)
    return sum(count_chars(child, include_block_code, counter) for child in _children(node))


def count_code_chars(node, counter):
    name = type(node).__name__
    if name in CODE_TOKENS:
        return count_chars(node, counter=counter)
    if name in SKIPPED_TOKENS:
        return 0
    return sum(count_code_chars(child, counter) for child in _children(node))


def prose_chars(node):
    return count_chars(node, include_block_code=False)


# ── Structure walkers (all return lists of char counts) ──────────────────────

def section_chars(doc):
    """Body chars of each section; content before the first heading is a section too."""
    sections, current = [], 0
    for node in doc.children or []:
        if type(node).__name__ in ("Heading", "SetextHeading"):
            sections.append(current)
            current = 0
        else:
            current += count_chars(node)
    sections.append(current)
    return [n for n in sections if n > 0]


def paragraph_and_list_chars(node, paragraphs, lists):
    """Collect paragraph chars and whole-list chars.

    Lists are not descended into: paragraphs inside list items are list content,
    and nested lists are part of their top-level list.
    """
    name = type(node).__name__
    if name == "Paragraph":
        paragraphs.append(prose_chars(node))
    elif name == "List":
        lists.append(prose_chars(node))
    elif name in ("Document", "Quote"):
        for child in _children(node):
            paragraph_and_list_chars(child, paragraphs, lists)


def list_item_chars(node, items):
    """Chars of each list item's own paragraphs, at any nesting depth."""
    name = type(node).__name__
    if name == "ListItem":
        items.append(sum(prose_chars(c) for c in _children(node) if type(c).__name__ == "Paragraph"))
    if name in CODE_TOKENS or name in SKIPPED_TOKENS or name == "Table":
        return
    for child in _children(node):
        list_item_chars(child, items)


# ── Top level ────────────────────────────────────────────────────────────────

def read_input(path):
    if path == "-":
        return sys.stdin.buffer.read().decode("utf-8")
    return Path(path).read_text(encoding="utf-8")


def analyze(path, chars_per_word=CHARS_PER_WORD):
    text = read_input(path)

    match = FRONT_MATTER.match(text)
    if match:
        text = text[match.end():]

    with HtmlRenderer():  # registers HTML tokens so they can be skipped
        doc = Document(text)

    total_chars = count_chars(doc)
    non_space = count_chars(doc, counter=non_space_chars)
    code_non_space = count_code_chars(doc, non_space_chars)
    sections, paragraphs, lists, items = section_chars(doc), [], [], []
    paragraph_and_list_chars(doc, paragraphs, lists)
    list_item_chars(doc, items)

    def avg(values):
        return round(sum(values) / len(values) / chars_per_word, 1) if values else None

    return {
        "file": "<stdin>" if path == "-" else str(path),
        "normalized_words": round(total_chars / chars_per_word),
        "code_percent": round(100 * code_non_space / non_space) if non_space else 0,
        "sections": len(sections),
        "avg_section_words": avg(sections),
        "avg_paragraph_words": avg(paragraphs),
        "avg_list_words": avg(lists),
        "avg_list_item_words": avg(items),
    }


def format_text(result):
    lines = [result["file"]]
    for key, value in result.items():
        if key != "file":
            lines.append(f"  {key:<22}{'-' if value is None else value}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Measure size and structure of markdown documents.")
    parser.add_argument("files", nargs="*", default=["-"], metavar="FILE",
                        help="markdown files; - or none reads standard input")
    parser.add_argument("--json", action="store_true", help="print a JSON array")
    parser.add_argument("--chars-per-word", type=float, default=CHARS_PER_WORD,
                        help=f"normalization constant (default: {CHARS_PER_WORD})")
    args = parser.parse_args()

    results, failed = [], False
    for path in args.files:
        try:
            results.append(analyze(path, args.chars_per_word))
        except (OSError, UnicodeDecodeError) as exc:
            print(f"error: {path}: {exc}", file=sys.stderr)
            failed = True

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("\n\n".join(format_text(r) for r in results))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
