# Gmail Attachment Search Script

## Overview

A command-line Python script that authenticates with Gmail via OAuth 2.0, searches for emails matching a user-supplied query string, filters for messages that have attachments, and prints the 3 most recent matching results to stdout.

## Usage

```
python gmail_search.py "<query>"
```

Example:
```
python gmail_search.py "from:boss@example.com invoice"
```

## Behavior

1. The script accepts one positional argument: a Gmail search query string (same syntax as the Gmail search bar).
2. It authenticates with the Gmail API (see Authentication).
3. It searches **all mail** (not just the inbox) using the provided query. To restrict to inbox, the user can include `in:inbox` in their query.
4. Results are fetched in reverse-chronological order (newest first) using the `q` parameter of the Gmail API's `messages.list` endpoint.
5. **Attachment detection**: a message part counts as an attachment when it has a non-empty `filename` field in the Gmail API response. Inline parts (e.g. embedded images with no filename) are excluded.
6. The script pages through results in batches, stopping as soon as 3 emails with attachments are found or all results are exhausted. A hard cap of 500 messages examined prevents runaway API usage on broad queries.
7. For each of the 3 matching emails it prints:
   - Date sent
   - Sender (`From` header)
   - Subject
   - List of attachment filenames and their MIME types

## Authentication

Uses Google's OAuth 2.0 for installed applications with the `gmail.readonly` scope (least privilege). On first run a browser window opens for authorization; the resulting token is saved to `token.json` and refreshed automatically on subsequent runs.

**Why OAuth over App Password**: App Passwords require disabling 2-Step Verification enforcement and grant broader account access. OAuth with a read-only scope is the recommended, more secure path.

Requires a `credentials.json` file (OAuth client secrets downloaded from Google Cloud Console) in the working directory.

## Output Format

Plain text to stdout, one block per email:

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

If fewer than 3 matches are found: `(Found N email(s) with attachments matching your query.)`

If none: `No emails with attachments found for query: "<query>"`

## Error Handling

- Missing `credentials.json`: print a clear message explaining how to obtain it, exit with code 1.
- Gmail API errors (quota exceeded, network failure): print the error and exit with code 1.
- Invalid or empty query string: print usage hint and exit with code 1.

## Design Choices

**Gmail API over IMAP**: The Gmail API supports the full Gmail query syntax (labels, operators, etc.) and returns structured part metadata, making attachment detection straightforward. IMAP requires manual MIME parsing and does not support Gmail-specific search operators.

**Plain-text output**: Chosen for simplicity and easy piping/grepping. JSON output is out of scope but trivial to add later.

## Assumptions & Risks

- **Google Cloud project required**: the user must create a project, enable the Gmail API, and download `credentials.json`. This is a one-time setup step not automated by the script.
- **API quota**: Gmail API has a default limit of 250 quota units/second per user. Fetching message metadata is 5 units/call; the 500-message hard cap keeps usage well within limits for typical use.
- **Attachment definition**: only parts with a `filename` field are counted. Encrypted or S/MIME messages may present all content as a single opaque part — those will not show individual attachments.

## Setup

Install dependencies:
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
