# Gmail Attachment Search Script

## Overview

CLI Python script: searches Gmail with a user-provided query and returns the 3 most recent emails containing file attachments (inline images excluded).

## Functional Requirements

- Accept a query string as a CLI argument
- Authenticate via OAuth 2.0 and search Gmail for matching emails with attachments
- Display each result's sender, date, subject, and attachment filenames
- If fewer than 3 matches exist, show what was found; if none, print a clear message

## Interface

```
python search_attachments.py "<query>"
```

Output per email:
```
Date:        2024-03-15
From:        boss@company.com
Subject:     Q1 Invoice
Attachments: invoice_q1.pdf, receipt.png
```

## Authentication

- OAuth 2.0, read-only scope (`gmail.readonly`)
- `credentials.json` required in working directory (obtained from Google Cloud Console)
- Token cached in `token.json`; auto-refreshed when expired

## Attachment Detection

Appends `has:attachment` to the query for server-side filtering, avoiding full MIME inspection of every result. Fetches up to 20 messages; reads MIME parts to extract filenames, skipping `Content-Disposition: inline` parts. Reports up to 3 results from those 20.

## Error Handling

- Missing `credentials.json`: print setup instructions, exit non-zero
- Unrefreshable token: delete `token.json` and re-authenticate
- API or network error: print error message, exit non-zero
- No results: print `No matching emails with attachments found.`

## Dependencies

`google-auth`, `google-auth-oauthlib`, `google-api-python-client`

## Design Decisions and Exclusions

Server-side `has:attachment` filtering reduces API calls vs. client-side MIME inspection.

Excluded: saving attachments to disk, pagination past 20 results, multiple accounts, GUI.
