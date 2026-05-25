# Gmail Attachment Search — Specification

## Overview

A command-line Python script that accepts a search query, searches the user's Gmail inbox for matching emails that have attachments, and prints a summary of the 3 most recent results.

---

## Inputs

| Input | Source | Description |
|-------|--------|-------------|
| `query` | CLI argument (positional) | Gmail search query string (e.g. `"from:boss@example.com"`) |

If no query is provided, the script prints a usage message and exits with code 1.

---

## Outputs

For each of the (up to 3) matching threads/messages, print to stdout:

```
Subject:  <subject>
From:     <sender>
Date:     <received date, ISO 8601>
Snippets: <message snippet>
Attachments:
  - <filename> (<MIME type>, <size in KB>)
  ...
```

Entries are separated by a blank line. Most-recent first.

If fewer than 3 results are found, print however many exist. If none are found, print:

```
No emails with attachments found for query: "<query>"
```

---

## Behaviour

1. Append `has:attachment` to the user-supplied query before searching, so only emails with attachments are matched.
2. Retrieve up to 3 threads matching the combined query, ordered by most-recent first (Gmail default).
3. For each thread, inspect the most-recent message within it.
4. For each such message, list every attachment part (non-inline parts with a filename).
5. Do **not** download attachment content — only report metadata (filename, MIME type, size).

---

## Authentication

- Use the Gmail MCP tools already available in the environment (`mcp__claude_ai_Gmail__*`).
- No separate OAuth flow is needed; authentication is handled by the MCP layer.

---

## Error handling

| Condition | Behaviour |
|-----------|-----------|
| Gmail API / MCP error | Print error message to stderr, exit code 2 |
| No results | Print "no results" message to stdout, exit code 0 |
| Missing query argument | Print usage to stderr, exit code 1 |

---

## Constraints

- Python 3.9+, standard library only (no third-party packages beyond what the MCP client provides).
- Single file: `search_attachments.py`.
- No interactive prompts after launch.
- Output must be human-readable plain text (no JSON, no colour codes).

---

## Out of scope

- Downloading or saving attachments.
- Pagination beyond the first 3 results.
- Sending or modifying emails.
- GUI or web interface.
