# Gmail Attachment Search Script

## Overview

A command-line Python script that searches a user's Gmail inbox using a provided query string and returns the three most recent matching emails that contain file attachments (not inline images).

## Functional Requirements

- Accept a search query string as a command-line argument
- Authenticate with the Gmail API using OAuth 2.0
- Search Gmail for messages matching the query, restricted to those with attachments
- Return the three most recent such messages, ordered by date received (newest first)
- Display for each result: sender, date, subject, and attachment filenames
- If fewer than 3 matches exist, display however many are found; if none, print a clear message

## Interface

```
python search_attachments.py "<query>"
```

Example:
```
python search_attachments.py "from:boss@company.com invoice"
```

Output format (one block per email):
```
Date:        2024-03-15
From:        boss@company.com
Subject:     Q1 Invoice
Attachments: invoice_q1.pdf, receipt.png
```

## Authentication

- Use OAuth 2.0 with read-only scope (`gmail.readonly`)
- Require a `credentials.json` file in the working directory (downloaded from Google Cloud Console)
- Cache the token in `token.json` in the working directory; refresh automatically when expired
- If `credentials.json` is missing, print a clear setup instruction and exit with a non-zero code

## Attachment Detection

The script appends `has:attachment` to the user's query before sending it to the Gmail API, so Gmail performs attachment filtering server-side rather than fetching all messages and inspecting their MIME structure. After retrieving results, the script reads each message's MIME parts to extract attachment filenames, skipping parts with `Content-Disposition: inline` (e.g. embedded images).

The script fetches up to 20 results from the API in a single request. If fewer than 3 of those have non-inline attachments, it reports however many were found rather than paginating further.

## Error Handling

- Missing `credentials.json`: print setup instructions and exit non-zero
- Expired or revoked token that cannot be refreshed: delete `token.json`, prompt re-authentication
- API or network error: print the error message and exit non-zero
- No matching results: print `No matching emails with attachments found.`

## Dependencies

- `google-auth`, `google-auth-oauthlib`, `google-api-python-client`
- No other third-party libraries

## Design Decisions and Exclusions

Server-side `has:attachment` filtering is preferred over client-side MIME inspection of every result because it reduces API calls and bandwidth. A service account was not considered since the script targets individual users accessing their own mailbox.

Excluded: downloading or saving attachments to disk, pagination past 20 results, support for multiple Gmail accounts, any GUI or interactive interface.
