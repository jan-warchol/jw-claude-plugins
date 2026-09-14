#!/usr/bin/env python3
"""Measure size of mermaid diagrams.

Metrics per diagram:
  nodes        flowchart nodes, sequence participants, or classes
  connections  flowchart links, sequence messages, or class relationships;
               flowchart `A & B --> C` counts as 2
  groups       flowchart subgraphs; sequence boxes and blocks (loop, alt, opt,
               par, critical, break, rect); class namespaces
  normalized_words
               normalized words (alphanumeric chars / CHARS_PER_WORD) of the
               visible text: labels, messages, notes, members, titles. Keywords,
               arrows, styling and IDs hidden behind a label are not counted.

Parsed types: flowchart (graph), sequenceDiagram, classDiagram. For other types
only an approximate word count is given: all alphanumeric chars except the
header line and comments. Lines a parser does not understand are listed in
`unparsed_lines`.

Input: .mmd files, or markdown files (every ```mermaid block is a diagram).
With no FILE, or when FILE is -, standard input is read; it is treated as
markdown if it contains a ```mermaid block, otherwise as a single diagram.
See DESIGN.md for the rationale.

Usage:
  mermaid-metrics.py [--json] [--chars-per-word N] [FILE ...]
"""

import argparse
import json
import re
import sys
from pathlib import Path

CHARS_PER_WORD = 6

MARKDOWN_BLOCK = re.compile(r"^[ \t]*(```|~~~)[ \t]*mermaid[^\n]*\n(.*?)^[ \t]*\1[ \t]*$", re.DOTALL | re.MULTILINE)
COMMENT = re.compile(r"^[ \t]*%%.*$", re.MULTILINE)
FRONT_MATTER = re.compile(r"\A\s*---[ \t]*\n(.*?)^---[ \t]*$", re.DOTALL | re.MULTILINE)
FRONT_MATTER_TITLE = re.compile(r"^title:[ \t]*(.*)$", re.MULTILINE)
HTML_TAG = re.compile(r"<[^>]*>")


def alnum_chars(text):
    return sum(1 for c in text if c.isalnum())


def label_chars(text):
    return alnum_chars(HTML_TAG.sub(" ", text))


class Diagram:
    """Counters shared by all diagram parsers."""

    def __init__(self, body):
        self.body = body
        self.node_chars = {}   # node id -> chars of its label (or id)
        self.connections = 0
        self.groups = 0
        self.other_chars = 0   # all visible text that is not a node label
        self.unparsed = []

    def add_node(self, node_id, label=None):
        """Register a node; a label overrides earlier ones, a bare reference does not."""
        if label is not None:
            self.node_chars[node_id] = label_chars(label)
        else:
            self.node_chars.setdefault(node_id, alnum_chars(node_id))

    def add_text(self, text):
        self.other_chars += label_chars(text or "")

    def chars(self):
        return sum(self.node_chars.values()) + self.other_chars

    def lines(self):
        for line in self.body.splitlines():
            if line.strip():
                yield line.strip()


# ── Flowchart ────────────────────────────────────────────────────────────────

NODE_ID = re.compile(r"[\w]+(?:-(?![-.>=])\w+)*")
# (opener, closer regex), longest openers first
SHAPES = [
    ("(((", r"\)\)\)"), ("((", r"\)\)"), ("([", r"\]\)"), ("[[", r"\]\]"), ("[(", r"\)\]"),
    ("{{", r"\}\}"), ("[/", r"[/\\]\]"), ("[\\", r"[/\\]\]"),
    ("(", r"\)"), ("[", r"\]"), ("{", r"\}"), (">", r"\]"),
]
FLOW_ARROW_END = r"(?:-{2,}>|-{2,}[ox](?!\w)|-{3,}|={2,}>|={3,}"
LINK = re.compile(r"\s*(?:\w+@)?<?" + FLOW_ARROW_END + r"|-\.+->?|~{3,})(?:\s*\|([^|]*)\|)?")
TEXT_LINK = re.compile(r"\s*<?(?:--|==|-\.)\s+([^\n]+?)\s*" + FLOW_ARROW_END + r"|\.-+>?)")
FLOW_KEYWORD_LINE = re.compile(r"(classDef|class|style|linkStyle|click|direction|accTitle|accDescr|end)\b[^\n]*")
STATEMENT_END = re.compile(r"[ \t]*(?=[;\n]|\Z)")
SUBGRAPH = re.compile(r"subgraph\b[ \t]*([^\n;]*)")
AT_LABEL = re.compile(r"""label\s*:\s*(?:"([^"]*)"|'([^']*)'|([^,}]*))""")
NODE_GROUP_SEPARATOR = re.compile(r"[ \t]*&[ \t]*")
CLASS_SUFFIX = re.compile(r":::[\w-]+")


class Flowchart(Diagram):
    """Scanner for flowchart statements: node groups joined by links.

    Statements are separated by newlines or `;`, but quoted labels may span lines,
    so this scans the whole body instead of going line by line.
    """

    def parse(self):
        self.text, self.pos = self.body, 0
        subgraph_ids = set()
        self.skip_blank()
        while self.pos < len(self.text):
            if not (self.parse_subgraph(subgraph_ids) or self.match(FLOW_KEYWORD_LINE) or self.parse_statement()):
                start = self.pos
                end = self.text.find("\n", self.pos)
                self.pos = len(self.text) if end == -1 else end
                self.unparsed.append(self.text[start:self.pos].strip())
            self.skip_blank()
        for sub in subgraph_ids:
            self.node_chars.pop(sub, None)
        return self

    def match(self, pattern):
        m = pattern.match(self.text, self.pos)
        if m:
            self.pos = m.end()
        return m

    def skip_blank(self, chars=" \t\r\n;"):
        while self.pos < len(self.text) and self.text[self.pos] in chars:
            self.pos += 1

    def parse_subgraph(self, subgraph_ids):
        m = self.match(SUBGRAPH)
        if not m:
            return False
        self.groups += 1
        title = m.group(1).strip()
        id_match = NODE_ID.match(title)
        if id_match and title[id_match.end():].lstrip().startswith("["):
            subgraph_ids.add(id_match.group())
            title = title[id_match.end():].strip()[1:].rstrip("]")
        elif id_match and id_match.end() == len(title):
            subgraph_ids.add(title)
        self.add_text(title)
        return True

    def parse_statement(self):
        """Parse one statement; on failure restore the state from before it."""
        saved = (self.pos, dict(self.node_chars), self.connections, self.other_chars)
        if self.parse_links() and self.match(STATEMENT_END):
            return True
        self.pos, self.node_chars, self.connections, self.other_chars = saved
        return False

    def parse_links(self):
        group = self.parse_node_group()
        if not group:
            return False
        while True:
            link = self.match(LINK) or self.match(TEXT_LINK)
            if not link:
                return True
            self.add_text(link.group(1))
            self.skip_blank(" \t")
            target = self.parse_node_group()
            if not target:
                return False
            self.connections += len(group) * len(target)
            group = target

    def parse_node_group(self):
        nodes = []
        while True:
            node = self.parse_node()
            if node is None:
                return None
            nodes.append(node)
            if not self.match(NODE_GROUP_SEPARATOR):
                return nodes

    def parse_node(self):
        m = self.match(NODE_ID)
        if not m:
            return None
        label = self.parse_shape_label()
        if label is None and self.text.startswith("@{", self.pos):
            label = self.parse_at_label()
        self.add_node(m.group(), label)
        self.match(CLASS_SUFFIX)
        return m.group()

    def parse_shape_label(self):
        for opener, closer in SHAPES:
            if not self.text.startswith(opener, self.pos):
                continue
            start = self.pos + len(opener)
            quoted = re.compile(r'\s*"(.*?)"\s*(' + closer + ")", re.DOTALL).match(self.text, start)
            if quoted:
                self.pos = quoted.end()
                return quoted.group(1)
            plain = re.compile(closer).search(self.text, start)
            if plain:
                self.pos = plain.end()
                return self.text[start:plain.start()]
        return None

    def parse_at_label(self):
        end = self.text.find("}", self.pos)
        if end == -1:
            return None
        props = self.text[self.pos + 2:end]
        self.pos = end + 1
        m = AT_LABEL.search(props)
        return next((g for g in m.groups() if g is not None), "") if m else None


# ── Sequence diagram ─────────────────────────────────────────────────────────

ACTOR = r"[^\s:<>+\-,;][^:<>+\-,;]*?"
PARTICIPANT = re.compile(r"(?:create\s+)?(?:participant|actor)\s+(" + ACTOR + r")\s*(?:@\{.*\})?(?:\s+as\s+(.+))?$")
MESSAGE = re.compile(
    r"(" + ACTOR + r")\s*(?:<<-{1,2}>>|-{1,2}(?:>>|>|x|\)))\s*[+-]?\s*(" + ACTOR + r")\s*(?::(.*))?$")
SEQ_NOTE = re.compile(r"note\s+(?:left\s+of|right\s+of|over)\s+[^:]+:(.*)$", re.IGNORECASE)
SEQ_BLOCK = re.compile(r"(loop|alt|opt|par|par_over|critical|break)\b(.*)$")
SEQ_BLOCK_SECTION = re.compile(r"(else|and|option)\b(.*)$")
SEQ_BOX = re.compile(r"box\b(.*)$")
SEQ_COLOR = re.compile(r"rgba?\([^)]*\)|#[0-9a-fA-F]+|\btransparent\b")
SEQ_TITLE = re.compile(r"title\b:?(.*)$")
SEQ_KEYWORD_LINE = re.compile(
    r"(autonumber|activate|deactivate|destroy|end|links?|properties|details|accTitle|accDescr)\b")


class SequenceDiagram(Diagram):
    def parse(self):
        for line in self.lines():
            if m := PARTICIPANT.match(line):
                self.add_node(m.group(1).strip(), m.group(2))
            elif m := MESSAGE.match(line):
                self.add_node(m.group(1).strip())
                self.add_node(m.group(2).strip())
                self.add_text(m.group(3))
                self.connections += 1
            elif m := SEQ_NOTE.match(line):
                self.add_text(m.group(1))
            elif m := SEQ_BLOCK.match(line):
                self.groups += 1
                self.add_text(m.group(2))
            elif m := SEQ_BLOCK_SECTION.match(line):
                self.add_text(m.group(2))
            elif m := SEQ_BOX.match(line):
                self.groups += 1
                self.add_text(SEQ_COLOR.sub(" ", m.group(1)))
            elif line.startswith("rect"):
                self.groups += 1
            elif m := SEQ_TITLE.match(line):
                self.add_text(m.group(1))
            elif not SEQ_KEYWORD_LINE.match(line):
                self.unparsed.append(line)
        return self


# ── Class diagram ────────────────────────────────────────────────────────────

CLASS_NAME = r"`[^`]+`|\w+(?:~[^~\s]+~)?"
CLASS_ARROW = r"(?:<\||\*|o|<|\(\))?(?:--|\.\.)(?:\|>|\*|o|>|\(\))?"
RELATION = re.compile(
    r"(" + CLASS_NAME + r")\s*(?:\"([^\"]*)\")?\s*" + CLASS_ARROW
    + r"\s*(?:\"([^\"]*)\")?\s*(" + CLASS_NAME + r")\s*(?::(.*))?$")
CLASS_DECL = re.compile(
    r"class\s+(" + CLASS_NAME + r")\s*(?:\[\"([^\"]*)\"\])?\s*(?::::[\w-]+)?\s*(\{)?\s*(\})?\s*$")
MEMBER = re.compile(r"(" + CLASS_NAME + r")\s*:\s*(.+)$")
ANNOTATION = re.compile(r"<<(.+?)>>\s*(" + CLASS_NAME + r")?\s*$")
CLASS_NOTE = re.compile(r"note\s+(?:for\s+(" + CLASS_NAME + r")\s+)?\"(.*)\"\s*$")
NAMESPACE = re.compile(r"namespace\s+(\S+)\s*\{\s*$")
CLASS_KEYWORD_LINE = re.compile(r"(direction|style|classDef|cssClass|callback|click|link|accTitle|accDescr)\b")


class ClassDiagram(Diagram):
    def add_class(self, name, label=None):
        """Generic parameters are visible text but not part of the class id."""
        node_id = name.strip("`").split("~")[0]
        self.add_node(node_id, label)
        if label is None and "~" in name:
            self.node_chars[node_id] = alnum_chars(name)

    def parse(self):
        blocks = []  # stack of "class" / "namespace" for closing braces
        for line in self.lines():
            if blocks and blocks[-1] == "class":
                if line == "}":
                    blocks.pop()
                else:
                    self.other_chars += alnum_chars(line)  # member or <<annotation>>, not HTML
            elif line == "}" and blocks:
                blocks.pop()
            elif m := NAMESPACE.match(line):
                self.groups += 1
                self.add_text(m.group(1))
                blocks.append("namespace")
            elif m := CLASS_DECL.match(line):
                self.add_class(m.group(1), m.group(2))
                if m.group(3) and not m.group(4):
                    blocks.append("class")
            elif m := RELATION.match(line):
                self.add_class(m.group(1))
                self.add_class(m.group(4))
                self.add_text(" ".join(filter(None, (m.group(2), m.group(3), m.group(5)))))
                self.connections += 1
            elif m := ANNOTATION.match(line):
                self.add_text(m.group(1))
                if m.group(2):
                    self.add_class(m.group(2))
            elif m := CLASS_NOTE.match(line):
                self.add_text(m.group(2))
            elif m := MEMBER.match(line):
                self.add_class(m.group(1))
                self.add_text(m.group(2))
            elif not CLASS_KEYWORD_LINE.match(line):
                self.unparsed.append(line)
        return self


# ── Top level ────────────────────────────────────────────────────────────────

PARSERS = {
    "graph": Flowchart,
    "flowchart": Flowchart,
    "sequenceDiagram": SequenceDiagram,
    "classDiagram": ClassDiagram,
    "classDiagram-v2": ClassDiagram,
}


def split_header(source):
    """Return (diagram type, body after the header line, front matter title)."""
    title = ""
    front_matter = FRONT_MATTER.match(source)
    if front_matter:
        m = FRONT_MATTER_TITLE.search(front_matter.group(1))
        title = m.group(1).strip("\"' ") if m else ""
        source = source[front_matter.end():]
    source = COMMENT.sub("", source).strip()
    header, _, body = source.partition("\n")
    return (header.split() or ["unknown"])[0], body, title


def analyze_diagram(name, source, chars_per_word):
    kind, body, title = split_header(source)
    result = {"diagram": name, "type": kind}
    parser = PARSERS.get(kind)
    if parser is None:
        return result | {
            "nodes": None,
            "connections": None,
            "groups": None,
            "normalized_words": round((alnum_chars(body) + alnum_chars(title)) / chars_per_word),
            "note": "diagram type not parsed; words is approximate",
        }
    d = parser(body).parse()
    result |= {
        "nodes": len(d.node_chars),
        "connections": d.connections,
        "groups": d.groups,
        "normalized_words": round((d.chars() + alnum_chars(title)) / chars_per_word),
    }
    if d.unparsed:
        result["unparsed_lines"] = d.unparsed
    return result


def analyze_file(path, chars_per_word=CHARS_PER_WORD):
    if path == "-":
        name = "<stdin>"
        text = sys.stdin.buffer.read().decode("utf-8")
        is_markdown = MARKDOWN_BLOCK.search(text) is not None
    else:
        name = str(path)
        text = Path(path).read_text(encoding="utf-8")
        is_markdown = Path(path).suffix.lower() in (".md", ".markdown")
    if is_markdown:
        blocks = [m.group(2) for m in MARKDOWN_BLOCK.finditer(text)]
        return [analyze_diagram(f"{name}#{i}", b, chars_per_word) for i, b in enumerate(blocks, 1)]
    return [analyze_diagram(name, text, chars_per_word)]


def format_text(result):
    lines = [result["diagram"]]
    for key, value in result.items():
        if key == "diagram":
            continue
        if key == "unparsed_lines":
            lines.append(f"  {key}:")
            lines.extend(f"    {line}" for line in value)
        else:
            lines.append(f"  {key:<18}{'-' if value is None else value}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Measure size of mermaid diagrams.")
    parser.add_argument("files", nargs="*", default=["-"], metavar="FILE",
                        help=".mmd or markdown files; - or none reads standard input")
    parser.add_argument("--json", action="store_true", help="print a JSON array")
    parser.add_argument("--chars-per-word", type=float, default=CHARS_PER_WORD,
                        help=f"normalization constant (default: {CHARS_PER_WORD})")
    args = parser.parse_args()

    results, failed = [], False
    for path in args.files:
        try:
            results.extend(analyze_file(path, args.chars_per_word))
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
