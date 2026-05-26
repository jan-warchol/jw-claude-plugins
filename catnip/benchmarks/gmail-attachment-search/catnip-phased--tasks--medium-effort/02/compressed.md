# Gmail Attachment Search Script — Spec

## Overview

CLI Python script that authenticates with Gmail, searches the mailbox for a user-supplied query, and prints the three most recent matching emails that have attachments.

## Goals

- Accept a search query via `--query` / `-q` or an interactive prompt.
- Search via the Gmail API; filter to emails with at least one attachment.
- Return up to 3 results, newest-first.
- Display subject, sender, date, and attachment filename(s) per result.

## Non-goals

- Downloading attachment content.
- Sending, modifying, or deleting emails.
- Multiple accounts; reusable library.

## Authentication

- OAuth 2.0 via `google-auth-oauthlib`, scope `gmail.readonly`.
- First run opens a browser for consent; token cached in `token.json` (`0600` permissions; warn if world-readable).
- `credentials.json` (downloaded "installed application" client from Google Cloud Console) must exist in the working directory.

## Inputs

| Input | Source | Notes |
|-------|--------|-------|
| Search query | `--query`/`-q` or interactive prompt | `has:attachment` appended silently before API call |
| `credentials.json` | Working directory | OAuth client credentials |

## Core logic

1. Build/refresh credentials from `token.json` + `credentials.json`.
2. Append `has:attachment` to the query (reduces server-side candidate set; not shown to user).
3. Call `users.messages.list` with `maxResults=10`; no pagination.
4. For each message ID, call `users.messages.get` with `format=metadata` (headers `Subject`, `From`, `Date` plus MIME part metadata).
5. Walk `payload.parts` recursively; a message has a real attachment only if any part has a non-empty `filename` **and** `Content-Disposition: attachment`. Inline parts are excluded.
6. Collect up to 3 passing messages; display results.

## Output

```
─────────────────────────────────────────
Subject     : Re: Q2 budget review
From        : alice@example.com
Date        : Mon, 19 May 2026 14:32:07 +0200
Attachments : budget_v3.xlsx, notes.pdf
─────────────────────────────────────────
```

Fewer than 3 found: show all plus `(Only N matching email(s) found.)`.  
None found: `No emails matching "<query>" with attachments were found.`

## Error handling

- Missing `credentials.json`: explain how to obtain it, exit 1.
- OAuth or token refresh failure: print error, exit 1.
- API quota/network error: print error, exit 1.
- Zero results before filtering: treat as "none found."

## Design choices & trade-offs

**`has:attachment` injection vs. post-filtering:** Server-side filtering reduces API calls. Risk: Gmail's index and the script's MIME walk may disagree on edge-case MIME structures; affected messages are silently skipped.

**`format=metadata`:** Returns only headers and part descriptors — no body content, smaller payloads. Sufficient for all required output fields.

**No pagination:** `maxResults=10` is enough given `has:attachment` pre-filtering. Users needing more precise results should narrow their query.

## Assumptions & open questions

- User has Gmail API enabled in a Google Cloud project and `credentials.json` as an installed-app client.
- Browser is available for the initial OAuth flow.
- Gmail returns results newest-first by default (satisfies "last 3" without explicit sorting).
- `--max` flag and inline-image-as-attachment out of scope; count is hardcoded to 3; only `Content-Disposition: attachment` parts count.

## Dependencies

```
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

## File layout

```
gmail_search.py        # main script
credentials.json       # user-provided, not committed
token.json             # auto-generated, not committed
```

## Usage

```bash
python gmail_search.py --query "invoice 2026"
python gmail_search.py          # prompts for query
```
