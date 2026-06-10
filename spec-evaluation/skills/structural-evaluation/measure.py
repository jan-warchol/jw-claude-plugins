#!/usr/bin/env python3
"""
Compute structural metrics for markdown spec files.

Metrics reported per file:
  word_count            whitespace-delimited tokens containing a letter or digit
  avg_section_len       mean words per section (content between headings)
  avg_paragraph_len     mean words per paragraph-level block; a whole list or
                        table counts as one paragraph
  avg_bullet_len        mean words per individual list item (direct content only)
  code_char_ratio_pct   % of document chars inside code spans (fenced + inline)

Usage:
  uv run python measure.py file1.md [file2.md ...]

Output: JSON array, one object per file.
"""

import json
import sys
from pathlib import Path

from mistletoe import Document
from mistletoe.block_token import CodeFence
from mistletoe.span_token import InlineCode, RawText


# ── Text extraction ──────────────────────────────────────────────────────────

def _raw_text(node):
    """Recursively extract plain text from a node's inline content."""
    if isinstance(node, RawText):
        return node.content
    children = getattr(node, 'children', None) or []
    return ' '.join(_raw_text(child) for child in children)


def _word_count_of(node):
    text = _raw_text(node)
    return sum(1 for token in text.split() if any(c.isalnum() for c in token))


def _word_count_of_table(node):
    header_words = _word_count_of(node.header) if node.header else 0
    return header_words + sum(_word_count_of(row) for row in (node.children or []))


# ── AST walkers ──────────────────────────────────────────────────────────────

def _collect_code_chars(node):
    """Sum chars inside CodeFence content and InlineCode content nodes."""
    if isinstance(node, CodeFence):
        return len(node.content)
    if isinstance(node, InlineCode):
        return len(node.children[0].content)
    total = 0
    if type(node).__name__ == 'Table' and node.header:
        total += _collect_code_chars(node.header)
    for child in (getattr(node, 'children', None) or []):
        total += _collect_code_chars(child)
    return total


def _section_word_counts(doc):
    """
    Word count of content in each section (between headings).
    Content before the first heading is treated as its own section.
    """
    sections = []
    current = 0
    for node in (doc.children or []):
        name = type(node).__name__
        if name == 'Heading':
            sections.append(current)
            current = 0
        elif name == 'Table':
            current += _word_count_of_table(node)
        elif name not in ('ThematicBreak',):
            current += _word_count_of(node)
    sections.append(current)
    return [n for n in sections if n > 0]


def _paragraph_blocks(node):
    """
    Yield word count for each paragraph-level block.
    Paragraph → its words. List or Table (whole unit) → combined words.
    Heading, CodeFence, ThematicBreak → skipped.
    """
    name = type(node).__name__
    if name in ('Document', 'BlockQuote'):
        for child in (node.children or []):
            yield from _paragraph_blocks(child)
    elif name == 'Paragraph':
        yield _word_count_of(node)
    elif name == 'List':
        yield _word_count_of(node)
    elif name == 'Table':
        yield _word_count_of_table(node)


def _bullet_word_counts(node):
    """
    Word count of direct content per individual list item, at any nesting depth.
    Only the item's own paragraph content is counted, not nested sub-lists
    (those contribute their own entries when recursed).
    """
    counts = []
    name = type(node).__name__
    if name == 'ListItem':
        direct_words = sum(
            _word_count_of(child)
            for child in (node.children or [])
            if type(child).__name__ == 'Paragraph'
        )
        counts.append(direct_words)
        for child in (node.children or []):
            if type(child).__name__ == 'List':
                counts.extend(_bullet_word_counts(child))
    elif name != 'CodeFence':
        if name == 'Table' and node.header:
            pass  # no bullets inside tables
        else:
            for child in (getattr(node, 'children', None) or []):
                counts.extend(_bullet_word_counts(child))
    return counts


# ── Top-level metrics ────────────────────────────────────────────────────────

def word_count(text):
    """Count whitespace-delimited tokens that contain at least one letter or digit."""
    return sum(1 for token in text.split() if any(c.isalnum() for c in token))


def _avg(values):
    return round(sum(values) / len(values), 1) if values else None


def analyze(path):
    text = Path(path).read_text(encoding='utf-8')
    doc = Document(text)

    code_chars = _collect_code_chars(doc)
    code_ratio = round(code_chars / len(text) * 100) if text else 0

    sections   = _section_word_counts(doc)
    para_counts = list(_paragraph_blocks(doc))
    bullets     = _bullet_word_counts(doc)

    return {
        'file': str(path),
        'word_count': word_count(text),
        'avg_section_len': _avg(sections),
        'avg_paragraph_len': _avg(para_counts),
        'avg_bullet_len': _avg(bullets),
        'code_char_ratio_pct': code_ratio,
    }


def main():
    if len(sys.argv) < 2:
        print('Usage: measure.py <file.md> [file.md ...]', file=sys.stderr)
        sys.exit(1)

    results = []
    for arg in sys.argv[1:]:
        try:
            results.append(analyze(arg))
        except Exception as exc:
            print(f'Error: {arg}: {exc}', file=sys.stderr)

    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
