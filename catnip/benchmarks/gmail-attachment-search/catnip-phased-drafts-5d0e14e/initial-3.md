# Spec: Gmail Attachment Search Script

## Overview

A Python command-line script that searches Gmail for emails matching a user-provided query and returns the last 3 matching emails that contain attachments.

## Functional Requirements

- Accept a search query string as a command-line argument
- Search the user's Gmail inbox using the Gmail API
- Filter results to only include emails that have at least one attachment
- Return the 3 most recent matching emails (by date, newest first)
- For each matched email, display:
  - Subject
  - Sender
  - Date received
  - List of attachment filenames

## Non-Functional Requirements

- Authentication via OAuth2 using stored credentials (credentials.json / token.json)
- If no token exists, launch browser-based OAuth2 flow and persist the token
- Graceful error message if fewer than 3 matching emails are found (show however many exist)
- Graceful error message if no matches are found

## Out of Scope

- Downloading or saving attachments
- Pagination beyond 3 results
- Support for multiple Gmail accounts
- Any GUI or web interface

## Interface

```
python search_gmail_attachments.py "<query>"
```

Example:
```
python search_gmail_attachments.py "invoice from:acme.com"
```

Example output:
```
Found 3 emails with attachments matching "invoice from:acme.com":

1. Subject: Invoice #1042
   From: billing@acme.com
   Date: 2026-05-10
   Attachments: invoice_1042.pdf

2. Subject: Invoice #1031
   From: billing@acme.com
   Date: 2026-04-15
   Attachments: invoice_1031.pdf, receipt.png

3. Subject: Invoice #1020
   From: billing@acme.com
   Date: 2026-03-02
   Attachments: invoice_1020.pdf
```

## Implementation Notes

- Use the `google-api-python-client` and `google-auth-oauthlib` libraries
- Gmail API scopes required: `https://www.googleapis.com/auth/gmail.readonly`
- The Gmail API search query should append `has:attachment` to the user's query to pre-filter on the server side
- Use `messages.list` with `maxResults` to limit API calls, then fetch full message details with `messages.get` (format: `metadata`) to read headers and part structure
- Detect attachments by inspecting the `parts` of the message payload for parts with a non-empty `filename`
