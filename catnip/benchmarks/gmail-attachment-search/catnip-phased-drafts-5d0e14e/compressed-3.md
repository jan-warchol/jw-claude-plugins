# Spec: Gmail Attachment Search Script

## Overview

Python CLI script that searches Gmail for a user query and returns the 3 most recent emails with attachments.

## Functional Requirements

- Accept a query string as CLI argument; print usage and exit 1 if missing
- Search Gmail API, filtering to emails with at least one attachment (MIME part with non-empty `filename`; inline images without filenames excluded)
- Return up to 3 most recent matches (newest first); print informative message if none; exit 0 for empty results
- For each match, display: Subject, Sender, Date (YYYY-MM-DD), attachment filenames
- Exit 1 with error message on API or auth failures

## Authentication

OAuth2 via `credentials.json` / `token.json`; launches browser flow if no token exists.

## Out of Scope

Downloading attachments, pagination, multiple accounts, GUI, MIME-type filtering.

## Interface

```
python search_gmail_attachments.py "<query>"
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
```

## Implementation Notes

- Libraries: `google-api-python-client`, `google-auth-oauthlib`; scope: `gmail.readonly`
- Append `has:attachment` to the query for server-side pre-filtering
- Fetch 10 candidate IDs via `messages.list`, then `messages.get(format='metadata', metadataHeaders=['Subject','From','Date'])` to avoid body transfer
- Detect attachments by walking `parts` tree for non-empty `filename` fields (local check kept alongside API filter due to occasional disagreement)

## Assumptions

- `credentials.json` must be present; if absent, script fails with a message directing the user to Google Cloud Console
- No fallback pagination if fewer than 3 attachment emails appear in the first 10 results
