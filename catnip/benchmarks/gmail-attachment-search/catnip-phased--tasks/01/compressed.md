# Gmail Attachment Search Script

## Overview

CLI Python script that uses the Gmail API to search emails matching a user-supplied query and prints the 3 most recent results that have attachments.

## Usage

```
python gmail_search.py "<query>"
```

Example:
```
python gmail_search.py "from:boss@example.com invoice"
```

## Behavior

1. Accepts one positional argument: a Gmail search query (same syntax as the Gmail search bar).
2. Authenticates with the Gmail API (see Authentication).
3. Searches **all mail** using the query. Add `in:inbox` to restrict to inbox.
4. Fetches results newest-first via `messages.list`.
5. **Attachment detection**: a part counts as an attachment when its `filename` field is non-empty; inline parts (no filename) are excluded.
6. Pages through results in batches; stops at 3 matches or 500 messages examined (hard cap against runaway API usage).
7. Prints for each match: date, sender, subject, and attachment filenames with MIME types.

## Authentication

OAuth 2.0 for installed apps, `gmail.readonly` scope. First run opens a browser for authorization; token saved to `token.json` and auto-refreshed thereafter.

**OAuth over App Password**: App Passwords require disabling 2-Step Verification and grant broader access; OAuth read-only is the more secure standard path.

Requires `credentials.json` (OAuth client secrets from Google Cloud Console) in the working directory.

## Output Format

Plain text to stdout:

```
--- Email 1 ---
Date:    Thu, 22 May 2025 14:30:00 +0000
From:    boss@example.com
Subject: Q2 Invoice
Attachments:
  - invoice_q2.pdf  (application/pdf)
  - receipt.png     (image/png)

--- Email 2 ---
...
```

Fewer than 3 found: `(Found N email(s) with attachments matching your query.)`

None found: `No emails with attachments found for query: "<query>"`

## Error Handling

- Missing `credentials.json`: print instructions for obtaining it, exit 1.
- Gmail API errors (quota, network): print the error, exit 1.
- Empty or missing query: print usage hint, exit 1.

## Design Choices

**Gmail API over IMAP**: supports full Gmail query syntax and structured part metadata; IMAP requires manual MIME parsing and lacks Gmail-specific operators.

**Plain-text output**: simple and pipeable. JSON is trivial to add later.

## Assumptions & Risks

- **Cloud project required**: user must create a GCP project, enable the Gmail API, and download `credentials.json` (one-time setup, not automated).
- **API quota**: 250 units/s limit; message metadata costs 5 units/call — the 500-message cap stays well within limits.
- **Attachment definition**: only parts with a `filename` field count. S/MIME messages may appear as a single opaque part with no listed attachments.

## Setup

```
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

| File | Purpose |
|---|---|
| `gmail_search.py` | Main script |
| `credentials.json` | OAuth client secrets (user-provided, not committed) |
| `token.json` | Cached access/refresh token (auto-generated, not committed) |

## Out of Scope

- Downloading attachment content.
- Support for multiple Gmail accounts.
- GUI or web interface.
- Pagination beyond 500 messages examined.
