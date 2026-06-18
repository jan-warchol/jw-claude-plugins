#!/usr/bin/env python3
"""Minimal MCP (Model Context Protocol) stdio server exposing a word-count tool.

Implements just enough of the JSON-RPC 2.0 / MCP handshake to be usable by
Claude Code. Stdlib only - no third-party dependencies, so it runs anywhere a
plain `python3` is available.

The `count_words` tool reports two numbers:
  - alphanumeric_words: whitespace-delimited tokens containing >=1 letter/digit
  - alphanumeric_characters: count of letter/digit characters

Both ignore punctuation and markdown formatting (### , 1. , |---|, *, etc.),
which is exactly why this is a better prose-length metric than `wc -w`.
"""
import json
import sys

SERVER_NAME = "markdown-wordcount"
SERVER_VERSION = "0.1.0"
DEFAULT_PROTOCOL = "2025-06-18"

TOOLS = [
    {
        "name": "count_words",
        "description": (
            "Measure the prose length of a markdown/text file (preferred) or raw text. "
            "Returns the number of alphanumeric words (whitespace-delimited tokens with at "
            "least one letter or digit) and the number of alphanumeric characters. "
            "Punctuation and markdown formatting are NOT counted, so this is the metric to "
            "use for compression work - do not use `wc`, which counts symbols and formatting. "
            "Prefer passing `path` over `text` so invocations stay cheap on context."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to a UTF-8 text file to measure. Preferred over `text`.",
                },
                "text": {
                    "type": "string",
                    "description": "Raw text to measure. Used only when `path` is omitted.",
                },
            },
        },
    }
]


def count(text):
    """Return (alphanumeric_words, alphanumeric_characters) for a string."""
    words = sum(1 for tok in text.split() if any(c.isalnum() for c in tok))
    chars = sum(1 for c in text if c.isalnum())
    return words, chars


def run_count_words(args):
    path = args.get("path")
    text = args.get("text")
    if path:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        source = path
    elif text is not None:
        source = "(inline text)"
    else:
        raise ValueError("Provide either `path` or `text`.")
    words, chars = count(text)
    return (
        f"source: {source}\n"
        f"alphanumeric_words: {words}\n"
        f"alphanumeric_characters: {chars}"
    )


def result(rid, payload):
    return {"jsonrpc": "2.0", "id": rid, "result": payload}


def error(rid, code, message):
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": message}}


def handle(msg):
    method = msg.get("method")
    rid = msg.get("id")

    if method == "initialize":
        proto = (msg.get("params") or {}).get("protocolVersion", DEFAULT_PROTOCOL)
        return result(rid, {
            "protocolVersion": proto,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
        })

    if method == "tools/list":
        return result(rid, {"tools": TOOLS})

    if method == "tools/call":
        params = msg.get("params") or {}
        name = params.get("name")
        if name != "count_words":
            return error(rid, -32602, f"Unknown tool: {name}")
        try:
            text = run_count_words(params.get("arguments") or {})
            return result(rid, {"content": [{"type": "text", "text": text}], "isError": False})
        except Exception as exc:  # report tool failures as tool errors, not protocol errors
            return result(rid, {"content": [{"type": "text", "text": f"Error: {exc}"}], "isError": True})

    if method == "ping":
        return result(rid, {})

    # Notifications (no id) need no response; unknown requests get method-not-found.
    if rid is not None:
        return error(rid, -32601, f"Method not found: {method}")
    return None


def serve():
    """Run the MCP stdio loop (newline-delimited JSON-RPC)."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle(msg)
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


def cli(paths):
    """Run as a plain CLI: print counts for each given file path."""
    for path in paths:
        with open(path, "r", encoding="utf-8") as f:
            words, chars = count(f.read())
        print(f"{path}: alphanumeric_words={words} alphanumeric_characters={chars}")


if __name__ == "__main__":
    # With file arguments -> standalone CLI; with no arguments -> MCP stdio server.
    if len(sys.argv) > 1:
        cli(sys.argv[1:])
    else:
        serve()
