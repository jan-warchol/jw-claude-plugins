# Gmail Attachment Search Script

## Goal

CLI utility to locate recent Gmail emails with attachments matching a search query, without
opening a browser. Useful for quickly surfacing emails containing files (invoices, reports, etc.).

## Requirements

- Accepts a Gmail search query as a CLI argument (same syntax as Gmail's web search box).
- Returns the 3 most recent matching emails that have at least one attachment.
- Output per email: date, sender, subject, and attachment filenames.
- If fewer than 3 matches exist, print available results plus a clear notice — no hard error.
- OAuth2 browser consent flow on first run; token persisted locally for reuse.
- Read-only access; no attachment downloading, no message modification.

Out of scope: attachment downloading, filtering by type/size, pagination UI.

## Solution

Dependencies: `google-api-python-client`, `google-auth-oauthlib`. User provides `credentials.json`
(from Google Cloud Console); token cached as `token.json`.

Flow:

1. Load/refresh OAuth token; open browser consent flow if absent. Scope: `gmail.readonly`.
2. Append `has:attachment` to user query; call `users.messages.list` requesting ~20 results.
3. For each candidate (newest-first), call `users.messages.get` (format=`metadata`); confirm
   attachment by checking for MIME parts with `Content-Disposition: attachment`.
4. Collect until 3 confirmed hits, then print formatted output.

Single-file script. Fetching 20 candidates buffers against rare `has:attachment` over-matching.

## Unknowns

- **Inline images**: only `Content-Disposition: attachment` parts count; inline images excluded.
- **API quota**: fetching ~20 messages per run is well within free-tier limits.
- **Multi-part nesting**: MIME parts may be nested; traversal must recurse into `multipart/*`
  parts.
