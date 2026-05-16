# Gmail Attachment Search Script — Specification

## Overview

A command-line Python script that accepts a Gmail search query from the user, searches the authenticated user's Gmail account, and returns the three most recent matching emails that contain at least one attachment. For each result it prints a summary of the message and lists the attachment filenames.

---

## Goals

- Simple single-file script, no web server or daemon required.
- Authenticates with Gmail via OAuth 2.0 and caches credentials locally.
- Returns exactly the **last 3** emails (newest first) that match the query **and** have at least one attachment.
- Prints human-readable output to stdout.

---

## Non-Goals

- Downloading or saving attachment content to disk.
- Sending, deleting, or modifying any messages.
- Pagination beyond what is needed to find 3 matching messages with attachments.
- Support for non-Gmail IMAP providers.

---

## Authentication

### Method
OAuth 2.0 with the Gmail API (read-only scope).

### Scope
```
https://www.googleapis.com/auth/gmail.readonly
```

### Credential flow
1. The script looks for `credentials.json` (a Google Cloud OAuth client secrets file) in the working directory.
2. On first run it opens a browser-based consent screen and stores the resulting token in `token.json` (same directory).
3. On subsequent runs it loads `token.json` and refreshes automatically when expired.
4. If `credentials.json` is missing, the script exits with a clear error message pointing the user to the Google Cloud Console.

### Files
| File | Purpose | Committed to VCS? |
|---|---|---|
| `credentials.json` | OAuth client secrets (download from GCP) | No — add to `.gitignore` |
| `token.json` | Cached access/refresh token | No — add to `.gitignore` |

---

## Inputs

### Command-line argument
```
python search_attachments.py "<gmail-query>"
```

The query is a single positional argument. It accepts any syntax supported by the Gmail search interface (e.g., `from:boss@example.com`, `subject:invoice`, `after:2024/01/01`). Quoting is the user's responsibility.

### Optional flags
| Flag | Default | Description |
|---|---|---|
| `--count N` | `3` | Number of results to return (minimum 1, maximum 10). |
| `--max-scan N` | `50` | Maximum number of Gmail API results to scan for attachments before giving up. |

---

## Output

### Success — results found

For each of the (up to 3) matching messages, print a block:

```
────────────────────────────────────────
Result 1 of 3
Date:    Mon, 12 May 2025 09:14:33 +0000
From:    Alice Smith <alice@example.com>
Subject: Q1 Invoices
Message-ID: 18f3a2b1c4d5e6f7

Attachments (2):
  • invoice_march.pdf  (application/pdf, 142 KB)
  • invoice_april.pdf  (application/pdf, 98 KB)
```

### Success — fewer than 3 results

Print the results found, then:
```
Only 2 message(s) with attachments found within the scanned window.
```

### No results
```
No messages with attachments matched your query.
```

### Error states (see Error Handling section)
Errors are printed to stderr and the script exits with a non-zero code.

---

## Core Logic

### Step-by-step algorithm

1. **Parse arguments.** Validate `--count` and `--max-scan` ranges; exit with usage error if invalid.
2. **Authenticate.** Load or obtain OAuth credentials (see Authentication).
3. **Search Gmail.**
   - Call `users.messages.list` with the user's query.
   - Request up to `--max-scan` message IDs, sorted by newest first (default Gmail ordering).
   - If the result set is empty, print "no results" and exit 0.
4. **Filter for attachments.**
   - Iterate through returned message IDs in order.
   - For each ID, call `users.messages.get` with `format=metadata` and `metadataHeaders=["From","Date","Subject"]`.
   - Inspect the message's `payload` parts recursively: a part has an attachment if `part.filename` is non-empty **and** `part.body.attachmentId` is present.
   - If at least one attachment part is found, record the message.
   - Stop when `--count` matching messages have been collected or `--max-scan` messages have been examined, whichever comes first.
5. **Print results** in the format described above.

### Attachment detection rule

A MIME part is considered an attachment when **both** conditions hold:
- `part["filename"]` is a non-empty string.
- `part["body"]["attachmentId"]` is present (i.e., the content is stored separately, not inline).

Inline images embedded via `Content-Disposition: inline` with a `Content-ID` are excluded (they are decorative, not user-facing attachments).

### Size reporting

Attachment size is taken from `part["body"]["size"]` (bytes). Display in KB (1 decimal place) if < 1 MB, otherwise in MB (2 decimal places).

---

## Dependencies

| Package | Version constraint | Purpose |
|---|---|---|
| `google-api-python-client` | `>=2.0` | Gmail REST API wrapper |
| `google-auth-httplib2` | `>=0.1` | HTTP transport for google-auth |
| `google-auth-oauthlib` | `>=1.0` | OAuth 2.0 flow |

No third-party parsing or display libraries are used. All are installable via pip:

```
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

A `requirements.txt` is included listing the above with minimum versions pinned.

---

## Error Handling

| Condition | Behaviour |
|---|---|
| `credentials.json` missing | Print setup instructions to stderr, exit 1. |
| OAuth flow cancelled by user | Print "Authentication cancelled." to stderr, exit 1. |
| Token refresh fails (revoked) | Delete `token.json`, print "Re-authentication required." to stderr, exit 1. |
| Gmail API quota exceeded (429) | Print error with retry-after hint to stderr, exit 1. No automatic retry. |
| Gmail API other HTTP error | Print status code and message to stderr, exit 1. |
| Query argument missing | Print usage string to stderr, exit 2. |
| `--count` / `--max-scan` out of range | Print validation error to stderr, exit 2. |

---

## File Layout

```
gmail-attachments/
├── search_attachments.py   # Main script (single file)
├── requirements.txt
├── .gitignore              # Excludes credentials.json, token.json
└── spec.md                 # This document
```

---

## Usage Examples

```bash
# Find last 3 emails matching "invoice" that have attachments
python search_attachments.py "invoice"

# Search emails from a specific sender, return up to 2 results
python search_attachments.py "from:finance@acme.com" --count 2

# Combine Gmail operators as usual
python search_attachments.py "subject:report after:2025/01/01"

# Increase scan window if inbox is large
python search_attachments.py "has:attachment label:inbox" --max-scan 100
```

---

## Out of Scope / Future Considerations

- Downloading attachment bytes to disk (would require the `drive` scope or `gmail.modify` scope).
- Interactive query builder / TUI.
- Multiple Gmail accounts in one invocation.
- Async/concurrent API calls (not needed for this scale).
- Unit tests (could be added using `unittest.mock` to stub the API client).
