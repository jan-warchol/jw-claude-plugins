# Gmail Attachment Search Script — Spec

## Overview

A command-line Python script that accepts a Gmail search query from the user and returns the three most recent matching emails that contain at least one attachment. For each result, the script prints a summary of the email and lists its attachments.

## Authentication

- Uses the Gmail API via `google-auth` and `google-api-python-client`.
- OAuth 2.0 flow with a `credentials.json` file (downloaded from Google Cloud Console).
- On first run, opens a browser for consent; stores the resulting token in `token.json` for subsequent runs.
- Required OAuth scope: `https://www.googleapis.com/auth/gmail.readonly`.

## Input

- **Search query**: provided as a command-line argument (required).
  - Example: `python search_gmail.py "invoice from:accounting@example.com"`
  - The query uses Gmail's standard search syntax.

## Core Logic

1. Authenticate and build the Gmail API client.
2. Call `users.messages.list` with:
   - `q`: the user-supplied query string
   - `maxResults`: a fetch batch size (e.g. 20) to avoid fetching all messages upfront
3. For each message ID returned, fetch the full message (`users.messages.get` with `format=metadata` or `full`).
4. Check whether the message has any parts with a `filename` field (indicating an attachment).
5. Collect qualifying messages until 3 are found, or the result set is exhausted.
6. Messages are returned in the order Gmail provides them (most recent first by default).

## Output

For each of the (up to 3) matching emails, print:

- **Subject**
- **From**
- **Date**
- **Attachment names** (list of filenames)

Example output:

```
1. Subject: Q1 Invoice
   From: accounting@example.com
   Date: Mon, 12 May 2025 09:14:00 +0000
   Attachments: invoice_q1.pdf, terms.docx

2. Subject: Re: Contract Draft
   From: legal@example.com
   Date: Fri, 9 May 2025 17:03:22 +0000
   Attachments: contract_v2.pdf
```

If fewer than 3 emails with attachments are found, print however many were found (and note if none were found).

## Dependencies

- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

Listed in a `requirements.txt`.

## Error Handling

- Missing `credentials.json`: print a clear message directing the user to set up a Google Cloud project and download credentials.
- API errors: surface the error message and exit with a non-zero status code.
- No results found: print a friendly "No matching emails with attachments found." message.

## Out of Scope

- Downloading attachment content.
- Paginating beyond the initial fetch batch (if the first batch yields fewer than 3 hits, the script does not fetch additional pages).
- Support for multiple Gmail accounts simultaneously.
