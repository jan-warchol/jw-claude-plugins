# Gmail Attachment Search Script

## Overview

CLI Python script: takes a Gmail search query, finds the three most recent matching emails with attachments, prints their details.

## Functional Requirements

- Positional CLI argument: Gmail search query string
- Authenticate with Gmail API (OAuth 2.0, `gmail.readonly` scope)
- Append `has:attachment` to the query server-side; user need not include it
- Return up to 3 results (most recent first), each showing sender, subject, date, and attachment filenames

## Authentication

- Requires `credentials.json` (OAuth client secret from Google Cloud Console) in the working directory
- Caches access token in `token.json`; on first run opens a browser for authorization (prints URL if no browser available)

## Output

Plain-text to stdout, one block per email:

```
From: Alice <alice@example.com>
Subject: Q1 Invoice
Date: 2026-04-15
Attachments: invoice_q1.pdf, terms.docx
```

Prints however many results exist; if none: `No matching emails with attachments found.`

## Design Choices

- **Gmail API over IMAP**: supports full Gmail search syntax server-side, results sorted by date.
- **Server-side `has:attachment` filter**: faster than client-side MIME inspection. Inline images (`Content-Disposition: inline`) are excluded; only file attachments match.

## Error Handling

- Missing `credentials.json`: print setup instructions, exit non-zero
- Expired/invalid token: auto-delete `token.json` and re-authenticate
- Network error or API quota exceeded: print error message, exit non-zero

## Assumptions

- User has a Google Cloud project with Gmail API enabled; `credentials.json` is provided manually.
- Inline images not treated as attachments (revisit if needed).

## Dependencies

`google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`

## Out of Scope

Downloading attachments, modifying emails, pagination, GUI.
