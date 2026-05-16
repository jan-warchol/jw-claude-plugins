# Spec: Gmail Attachment Search Script

## Overview

A command-line Python script that accepts a search query from the user, searches Gmail for matching emails, and returns the 3 most recent results that contain attachments.

---

## Goals

- Accept a free-text or Gmail-syntax search query from the user.
- Use the Gmail MCP integration to execute the search.
- Filter results to only emails that contain at least one attachment.
- Return the 3 most recent qualifying emails with relevant metadata and attachment details.

---

## Non-Goals

- Downloading or saving attachment files locally.
- Sending, replying to, or modifying emails.
- Pagination beyond the first batch of results.
- Authentication handling (assumed to be pre-configured via MCP).

---

## Interface

### Input

The script accepts the search query as a command-line argument:

```
python search_gmail.py "<query>"
```

Example:

```
python search_gmail.py "invoice from:accountant@example.com"
```

If no argument is provided, the script prints usage instructions and exits with code 1.

### Output

For each of the (up to) 3 matching emails the script prints a block like:

```
--- Result 1 ---
Subject  : Q4 Invoice
From     : accountant@example.com
Date     : 2026-04-30
Thread ID: 18f3a2c...
Attachments (2):
  - invoice_q4.pdf  (application/pdf, 84 KB)
  - summary.xlsx    (application/vnd.ms-excel, 12 KB)
```

If fewer than 3 emails with attachments are found, all qualifying results are shown. If none are found, the script prints a clear message and exits with code 0.

---

## Implementation

### File

`search_gmail.py` — single-file script, no package structure needed.

### Dependencies

| Dependency | Purpose |
|---|---|
| `anthropic` Python SDK | Driving the Claude agent loop that calls Gmail MCP tools |
| `mcp__claude_ai_Gmail` MCP server | Gmail API access (search, thread retrieval) |

No external HTTP libraries are needed; all Gmail access goes through MCP tools.

### High-Level Flow

```
1. Parse CLI argument → raw_query (str)
2. Build Gmail query string:
     - Append "has:attachment" to raw_query so the Gmail API
       pre-filters results server-side.
     - Example: "invoice from:accountant@example.com has:attachment"
3. Call mcp__claude_ai_Gmail__search_threads with the combined query.
     - Request enough results to get at least 3 (e.g. maxResults=10
       as a safety buffer in case some threads lack attachments despite
       the filter).
4. For each returned thread (newest-first):
     a. Call mcp__claude_ai_Gmail__get_thread to fetch full thread data.
     b. Identify the most recent message in the thread.
     c. Inspect the message payload for MIME parts where
        "filename" is non-empty — these are attachments.
     d. If attachments found, add to results list.
     e. Stop once results list has 3 entries.
5. Format and print results (see Output section).
6. Exit 0 on success, 1 on argument error, 2 on API/tool error.
```

### Attachment Detection

An attachment is any MIME part satisfying **either** condition:

- `part["filename"]` is a non-empty string, **or**
- `part["headers"]` contains `Content-Disposition: attachment`.

For each attachment, record:
- `filename` (string, may be empty → show as `<unnamed>`)
- `mimeType` (string)
- `size` (bytes from `part["body"]["size"]`; format as KB or MB for display)

### Query Construction

Append `has:attachment` unconditionally to the user's query, joined by a space:

```python
gmail_query = f"{raw_query.strip()} has:attachment"
```

This keeps attachment filtering at the API layer, reducing data transfer and thread fetches.

### Result Ordering

`search_threads` returns threads in descending date order by default. The script processes them in that order and stops after collecting 3 results, so no client-side sorting is needed.

---

## Error Handling

| Situation | Behaviour |
|---|---|
| No CLI argument provided | Print usage, exit 1 |
| MCP tool call fails | Print error message with tool name and returned error, exit 2 |
| Zero results from search | Print "No emails with attachments found for query: `<query>`", exit 0 |
| Fewer than 3 results | Print all available results, note count in footer |
| Thread fetch fails for one result | Skip that thread, log a warning, continue to next |

---

## Example Runs

### Success — 3 results

```
$ python search_gmail.py "invoice"

Searching Gmail for: "invoice has:attachment"
Found 3 email(s) with attachments.

--- Result 1 ---
Subject  : Q4 Invoice
From     : accountant@example.com
Date     : 2026-04-30
Thread ID: 18f3a2cde91
Attachments (1):
  - invoice_q4.pdf  (application/pdf, 84 KB)

--- Result 2 ---
Subject  : March Invoice #0042
From     : billing@vendor.io
Date     : 2026-03-31
Thread ID: 18e1b0abc12
Attachments (2):
  - invoice_0042.pdf  (application/pdf, 61 KB)
  - receipt.png       (image/png, 204 KB)

--- Result 3 ---
Subject  : Fwd: Invoice for services
From     : manager@company.com
Date     : 2026-02-14
Thread ID: 18c9f33dd45
Attachments (1):
  - services_feb.pdf  (application/pdf, 45 KB)
```

### No results

```
$ python search_gmail.py "project:unicorn"

Searching Gmail for: "project:unicorn has:attachment"
No emails with attachments found for query: "project:unicorn"
```

### Missing argument

```
$ python search_gmail.py

Usage: python search_gmail.py "<gmail search query>"
Example: python search_gmail.py "invoice from:billing@example.com"
```

---

## Implementation Notes

- The script runs as a **Claude agent loop**: it instantiates an `anthropic.Anthropic` client, passes the task as a system prompt, and lets Claude issue the MCP tool calls (`search_threads`, `get_thread`) to complete the task. This avoids manually parsing the Gmail API response structure.
- Alternatively, the script can call MCP tools directly (not via agent loop) if the runtime exposes them as a Python-callable interface — the spec is compatible with both approaches.
- Keep the script self-contained in one file with no custom modules.
- Target Python 3.11+.
