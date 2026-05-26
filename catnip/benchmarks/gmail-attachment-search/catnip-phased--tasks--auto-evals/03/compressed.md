# Gmail Attachment Search Script — Spec

## Overview

A CLI Python script that takes a Gmail search query and prints the three most recent matching emails that have at least one attachment (subject, sender, date, filenames).

## Prerequisites

- Google Cloud project with Gmail API enabled; `credentials.json` downloaded from Google Cloud Console. The script does not automate this setup.
- Browser available on the machine for the initial OAuth consent flow.
- Python packages in `requirements.txt`: `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`.

## Authentication

- OAuth 2.0 using `credentials.json`. On first run, opens a browser for consent and saves the token to `token.json` (working directory) for reuse.
- Scope: `https://www.googleapis.com/auth/gmail.readonly`.
- Tokens are refreshed automatically; if refresh fails, the consent flow re-runs.

## Input

- **Search query**: required CLI argument using Gmail's standard search syntax.
  - Example: `python search_gmail.py "invoice from:accounting@example.com"`

## Core Logic

1. Authenticate and build the Gmail API client.
2. Call `users.messages.list` with the query and `maxResults=20`. 20 is enough to typically yield 3 attachment-bearing results without excess API calls.
3. For each message ID, fetch with `users.messages.get` at `format=full`. (`format=metadata` returns only headers, not MIME parts, so it cannot detect attachments.)
4. A message qualifies if any MIME part has a non-empty `filename` and is not inline content (`Content-Disposition: inline`, `text/*`, or `multipart/*` parts are excluded).
5. Collect until 3 qualify or the batch is exhausted. Results are ordered most-recent-first (Gmail's default).

## Output

Print Subject, From, Date, and attachment filenames for each result (up to 3):

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

If fewer than 3 qualify, print however many exist. If none, print `No matching emails with attachments found.`

## Error Handling

- Missing `credentials.json`: print setup instructions and exit.
- API errors: print the error message and exit non-zero.

## Design Decisions

- **No `has:attachment` auto-append**: the query is passed through unchanged; filtering happens in code. Silent query modification would confuse users who already include `has:attachment` or debug sparse results.
- **No pagination**: only the first 20-message batch is processed. If it yields fewer than 3 hits, the script stops. Keeps the script simple; users can refine the query.
- **`format=full` for all messages**: a two-pass approach (metadata first, full only for candidates) would save quota but adds complexity. With a 20-message batch, single-pass is simpler and fast enough.

## Out of Scope

- Downloading attachment content.
- Multiple Gmail accounts.
