# Gmail Attachment Search — Spec

## Overview

A command-line Python script that accepts a Gmail search query, searches the user's mailbox, and prints details for the 3 most recent matching emails that contain at least one attachment.

## Interface

```
python search_attachments.py "<query>"
```

- Single positional argument: a Gmail search query string (e.g. `"from:alice invoices"`)
- Exits with a non-zero status and a message if no matching emails with attachments are found

## Behavior

1. Accept the query string from the command line.
2. Search Gmail threads matching the query via the Gmail MCP tool (`search_threads`).
3. For each matched thread (most recent first), inspect messages for attachments (i.e. message parts with a `filename` and `body.attachmentId`).
4. Collect threads until 3 distinct threads with at least one attachment are found, or the result set is exhausted.
5. Print a summary for each of the (up to 3) found emails.

## Output Format

For each result, print a block like:

```
--- Email 1 ---
Subject : <subject>
From    : <sender>
Date    : <date>
Attachments:
  - <filename1> (<mime type>)
  - <filename2> (<mime type>)
```

## Implementation Notes

- Use the `mcp__claude_ai_Gmail__search_threads` tool to search, and `mcp__claude_ai_Gmail__get_thread` to retrieve full message details.
- Attachment detection: a message part is an attachment when it has a non-empty `filename` field.
- Only the 3 most recent matching threads (with attachments) are returned; older matches are ignored.
- No OAuth setup required — authentication is handled by the Gmail MCP tool.
- No external Python dependencies beyond the standard library are needed (all Gmail access goes through MCP tools, not the Gmail API directly).

## Error Handling

| Condition | Behavior |
|---|---|
| No query argument supplied | Print usage hint and exit 1 |
| Query returns no threads | Print "No emails found matching query." and exit 0 |
| Matching threads found but none have attachments | Print "No attachments found in matching emails." and exit 0 |
| MCP tool error | Print error message and exit 1 |

## Out of Scope

- Downloading or saving attachment content
- Pagination beyond the first page of search results
- Authentication / credential management
