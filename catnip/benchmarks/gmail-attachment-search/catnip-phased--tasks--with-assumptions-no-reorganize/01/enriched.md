# Spec: Gmail Attachment Search Script

## Objective

Build a simple Python CLI script that authenticates with Gmail, accepts a user-provided search query, and returns the 3 most recent emails matching that query that also have at least one attachment. The script lets users quickly locate recent attachments in their inbox without opening a browser.

## Requirements

**Must do:**
- Accept a Gmail search query string from the user (via CLI argument or interactive prompt)
- Authenticate with the user's Gmail account using OAuth2
- Search Gmail using the provided query, restricted to messages that have attachments
- Return up to 3 of the most recent matching emails; if fewer than 3 exist, return however many are found and print a note indicating the total found
- Display for each result: subject, sender, date, attachment filenames, and attachment sizes (sizes are required, not best-effort)
- Cache the OAuth token locally so the user is not re-prompted on subsequent runs
- Print clear setup instructions if `credentials.json` is missing

**Must not:**
- Download attachment content (display metadata only)
- Modify, move, or delete any emails
- Store or transmit credentials beyond what Google's OAuth2 flow requires

## Solution

**Authentication:** Use `google-auth-oauthlib` + `google-api-python-client` with a `credentials.json` file obtained from the Google Cloud Console. On first run, open a browser for the OAuth2 consent flow and persist the token to `token.json` in the working directory (same directory as the script, for simplicity — a production tool would use `~/.config/`). Request only the `https://www.googleapis.com/auth/gmail.readonly` scope to minimize permissions.

**Search:** Call `gmail.users().messages().list()` with `q=<user_query> has:attachment` and `maxResults=3`. Gmail's API returns results sorted newest-first by default, so the first 3 results are the most recent. If the user's query already contains `has:attachment`, appending it again is harmless — Gmail deduplicates it silently.

**Detail fetch:** For each message ID, call `gmail.users().messages().get()` with `format=metadata`, specifying `metadataHeaders=['Subject', 'From', 'Date']`. Walk `payload.parts` recursively to find parts where `filename` is non-empty and `body.size > 0`. Skip parts with `Content-Disposition: inline` to exclude embedded images (e.g., email signature logos) that are not user-intended attachments.

**Output:** Print results to stdout as plain text, one email per block, with a separator line between results. Example block:
```
From:    Alice <alice@example.com>
Date:    Wed, 28 May 2026 10:15:00 +0000
Subject: Q2 Report
Attachments:
  - report.pdf (142 KB)
  - data.xlsx (38 KB)
```

**Error handling:**
- Missing `credentials.json`: print setup instructions and exit with a non-zero code
- `google.auth.exceptions.RefreshError` (expired/revoked token): delete `token.json` and re-run the OAuth flow
- HTTP errors from the API (quota exceeded, network failure): print a human-readable message and exit; do not swallow exceptions silently

**Dependencies:**
- `google-api-python-client`
- `google-auth-oauthlib`
- `google-auth-httplib2`

**Entry point:** `gmail_search.py`, run as `python gmail_search.py "<query>"`.

## Alternative solutions considered

- **`imaplib` (IMAP):** Avoids the Google Cloud Console setup but requires enabling "Less secure app access" or app passwords, which Google is phasing out. Gmail API is the correct modern approach.
- **`simplegmail` / third-party wrappers:** Reduce boilerplate but add an opaque dependency. The official client library is thin enough that direct use is simpler for a small script.

## Out of scope

- Downloading or saving attachment files
- Pagination beyond the first 3 results
- Support for multiple Gmail accounts simultaneously
- Sending emails or any write operations
- Packaging as an installable CLI tool

## Uncertainty

- **Assumption — OAuth credentials setup:** The user must create a project in Google Cloud Console, enable the Gmail API, and download `credentials.json`. The script prints instructions if the file is missing, but the setup itself is out of scope.
- **Assumption — "returns" means prints to stdout:** No file output or structured data format (JSON, CSV) is implied unless the user later requests it.
- **Assumption — "last 3" means newest by received date:** Gmail's default API sort order (newest first) is used; no secondary sort is applied.
- **Inline attachment filtering:** Filtering by non-empty `filename` and skipping `Content-Disposition: inline` should correctly exclude signature images while including real attachments. Edge cases (malformed MIME, missing Content-Disposition) may still surface false positives.
- **API quota:** Gmail API has a free daily quota (1 billion quota units/day; `messages.list` costs 5 units, `messages.get` costs 5 units). A single script run costs ~20 units — well within limits for personal use.
