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
  section_words         body words per section (content between headings)
  paragraph_words       words per paragraph (list items excluded)
  list_words            words per top-level list, nested lists included
  list_item_words       words of an item's own text, nested lists excluded
  structured_percent    % of list and table text that reads as structure: each list
                        item or table cell counts as structured up to STRUCTURED_CAP
                        words, the rest of it counts as prose, like paragraphs
  anchor_gap_words      words of plain text between visual anchors (paragraph and
                        item starts, headings, emphasis, code, links, ...)

The distributions (section, paragraph, list, list item and anchor gap lengths) are
reported as the 15th, 50th and 85th percentile.

Usage:
  markdown-metrics.py [--json] [--chars-per-word N] [--structured-cap N] [FILE.md ...]

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
STRUCTURED_CAP = 13  # normalized words of a list item or table cell that count as structure
PERCENTILES = (15, 50, 85)

FRONT_MATTER = re.compile(r"\A(---|\+\+\+)[ \t]*\r?\n.*?^\1[ \t]*(\r?\n|\Z)", re.DOTALL | re.MULTILINE)

CODE_TOKENS = ("CodeFence", "BlockCode", "InlineCode")
SKIPPED_TOKENS = ("HtmlBlock", "HtmlSpan")
BLOCK_CODE_TOKENS = ("CodeFence", "BlockCode")
HEADING_TOKENS = ("Heading", "SetextHeading")
# Inline spans that stand out from plain text; their own text is not part of a gap.
ANCHOR_SPANS = ("Strong", "Emphasis", "Strikethrough", "InlineCode", "Link", "AutoLink", "Image")


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
        if type(node).__name__ in HEADING_TOKENS:
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


def structure_chars(node, cap):
    """(structured, prose) chars: list items and table cells up to cap chars each are
    structure, their excess and all paragraphs are prose. Headings and code are neither."""
    name = type(node).__name__
    if name == "Paragraph":
        return 0, prose_chars(node)
    if name == "Table":
        cells = [prose_chars(cell) for row in _children(node) for cell in _children(row)]
        return sum(min(c, cap) for c in cells), sum(max(0, c - cap) for c in cells)
    if name in HEADING_TOKENS or name in CODE_TOKENS or name in SKIPPED_TOKENS:
        return 0, 0
    structured = prose = 0
    if name == "ListItem":
        own = sum(prose_chars(c) for c in _children(node) if type(c).__name__ == "Paragraph")
        structured, prose = min(own, cap), max(0, own - cap)
    for child in _children(node):
        if name == "ListItem" and type(child).__name__ == "Paragraph":
            continue
        s, p = structure_chars(child, cap)
        structured, prose = structured + s, prose + p
    return structured, prose


def anchor_gaps(doc):
    """Chars of each run of plain text between two visual anchors, in reading order.

    Anchors are starts of paragraphs, list items, headings, code blocks, thematic breaks
    and emphasized, code or link spans. Anchored text (headings, spans, code) is not part
    of any gap. Tables are skipped: they are all anchors, with no plain text between.
    Empty gaps (two anchors in a row) are not reported.
    """
    gaps, current = [], 0

    def anchor():
        nonlocal current
        if current:
            gaps.append(current)
        current = 0

    def walk(node):
        nonlocal current
        name = type(node).__name__
        if name in SKIPPED_TOKENS:
            return
        if name == "RawText":
            current += alnum_chars(node.content)
            return
        if name in ("Paragraph", "ListItem"):
            anchor()
        elif name in HEADING_TOKENS or name in BLOCK_CODE_TOKENS or name in ANCHOR_SPANS \
                or name in ("Table", "ThematicBreak"):
            anchor()
            return
        for child in _children(node):
            walk(child)

    walk(doc)
    anchor()
    return gaps


# ── Top level ────────────────────────────────────────────────────────────────

def percentile(values, p):
    """Linear interpolation between closest ranks (like numpy's default)."""
    values = sorted(values)
    rank = (len(values) - 1) * p / 100
    low = int(rank)
    high = min(low + 1, len(values) - 1)
    return values[low] + (values[high] - values[low]) * (rank - low)


def read_input(path):
    if path == "-":
        return sys.stdin.buffer.read().decode("utf-8")
    return Path(path).read_text(encoding="utf-8")


def analyze(path, chars_per_word=CHARS_PER_WORD, structured_cap=STRUCTURED_CAP):
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
    structured, prose = structure_chars(doc, structured_cap * chars_per_word)

    def distribution(values):
        if not values:
            return None
        return {f"p{p}": round(percentile(values, p) / chars_per_word, 1) for p in PERCENTILES}

    return {
        "file": "<stdin>" if path == "-" else str(path),
        "normalized_words": round(total_chars / chars_per_word),
        "code_percent": round(100 * code_non_space / non_space) if non_space else 0,
        "sections": len(sections),
        "section_words": distribution(sections),
        "paragraph_words": distribution(paragraphs),
        "list_words": distribution(lists),
        "list_item_words": distribution(items),
        "structured_percent": round(100 * structured / (structured + prose)) if structured + prose else 0,
        "anchor_gap_words": distribution(anchor_gaps(doc)),
    }


def format_text(result):
    lines = [result["file"]]
    for key, value in result.items():
        if key == "file":
            continue
        if value is None:
            value = "-"
        elif isinstance(value, dict):
            value = "  ".join(f"{k} {v}" for k, v in value.items())
        lines.append(f"  {key:<22}{value}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Measure size and structure of markdown documents.")
    parser.add_argument("files", nargs="*", default=["-"], metavar="FILE",
                        help="markdown files; - or none reads standard input")
    parser.add_argument("--json", action="store_true", help="print a JSON array")
    parser.add_argument("--chars-per-word", type=float, default=CHARS_PER_WORD,
                        help=f"normalization constant (default: {CHARS_PER_WORD})")
    parser.add_argument("--structured-cap", type=float, default=STRUCTURED_CAP,
                        help="normalized words of a list item or table cell that count as "
                             f"structure (default: {STRUCTURED_CAP})")
    args = parser.parse_args()

    results, failed = [], False
    for path in args.files:
        try:
            results.append(analyze(path, args.chars_per_word, args.structured_cap))
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
