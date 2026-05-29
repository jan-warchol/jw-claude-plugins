# Spec: Gmail Attachment Search Script

## Overview

A Python command-line script that searches Gmail for emails matching a user-provided query and returns the last 3 matching emails that contain attachments. The primary use case is quickly locating recent attachments (e.g., invoices, receipts) without opening a browser.

## Functional Requirements

- Accept a search query string as a command-line argument; print a usage message and exit with code 1 if the argument is missing
- Search the user's Gmail inbox using the Gmail API
- Filter results to only include emails that have at least one attachment — defined as a MIME part with a non-empty `filename` field; inline images embedded without a filename (e.g., signature logos) are not counted
- Return the 3 most recent matching emails (by date, newest first — the default Gmail API ordering)
- For each matched email, display:
  - Subject
  - Sender
  - Date received (formatted as YYYY-MM-DD, parsed from the `Date` header)
  - List of attachment filenames
- If fewer than 3 matches exist, display however many do exist; if none exist, print an informative message; exit with code 0 in both cases since an empty result is valid
- Print a clear error message and exit with code 1 on API errors or authentication failures

## Non-Functional Requirements

- Authentication via OAuth2 using stored credentials (`credentials.json` / `token.json`)
- If no token exists, launch browser-based OAuth2 flow and persist the token; `credentials.json` must be present in the working directory for this to succeed

## Out of Scope

- Downloading or saving attachments
- Pagination beyond 3 results
- Support for multiple Gmail accounts
- Any GUI or web interface
- Filtering by attachment MIME type or filename pattern

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
- Append `has:attachment` to the user's query before sending to the API to pre-filter on the server side; this avoids fetching metadata for attachment-free messages
- Use `messages.list` with a small `maxResults` buffer (e.g., 10) to retrieve candidate IDs, then fetch each with `messages.get(format='metadata', metadataHeaders=['Subject','From','Date'])` — the `metadata` format is chosen over `full` to avoid transferring body content, keeping the tool fast even for large emails
- Detect attachments by walking the `parts` tree of the payload and collecting parts where `filename` is non-empty; this local check is kept alongside the `has:attachment` query because the API search operator and the parts structure can occasionally disagree
- Gmail API returns results newest-first by default; no explicit sort is required

## Assumptions and Risks

- **Assumption**: `credentials.json` is present in the working directory; if absent, the OAuth2 flow cannot start and the script will fail with a clear message directing the user to obtain it from Google Cloud Console
- **Risk**: Gmail API has a daily quota; each `messages.list` and `messages.get` call costs ~5 quota units, so fetching 10 candidate messages costs ~55 units — well within the default 1 billion units/day limit for normal use
- **Open question**: the spec requires exactly 3 results, but `has:attachment` pre-filtering means the first 10 API results should reliably contain 3 attachment emails for any non-trivial query; no fallback pagination is specified for queries that return fewer than 3 attachment emails in the first page
