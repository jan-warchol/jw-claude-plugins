# Gmail Attachment Search Script — Spec

## Overview

A command-line Python script that accepts a Gmail search query from the user and returns the three most recent matching emails that contain at least one attachment. For each result, the script prints a summary of the email and lists its attachment filenames.

## Prerequisites

- A Google Cloud project with the Gmail API enabled and `credentials.json` downloaded from the Google Cloud Console. Setup is a prerequisite; the script does not automate it.
- A browser available on the machine for the initial OAuth consent flow.
- Python packages (listed in `requirements.txt`):
  - `google-api-python-client`
  - `google-auth-httplib2`
  - `google-auth-oauthlib`

## Authentication

- OAuth 2.0 flow using the `credentials.json` file.
- On first run, opens a browser for consent; stores the resulting token in `token.json` (in the working directory) for subsequent runs.
- Required scope: `https://www.googleapis.com/auth/gmail.readonly`.
- Expired/invalid tokens are refreshed automatically; if refresh fails, the script re-runs the browser consent flow.

## Input

- **Search query**: provided as a command-line argument (required).
  - Example: `python search_gmail.py "invoice from:accounting@example.com"`
  - The query uses Gmail's standard search syntax.

## Core Logic

1. Authenticate and build the Gmail API client.
2. Call `users.messages.list` with:
   - `q`: the user-supplied query string
   - `maxResults: 20` — fetches the 20 most recent matching message IDs in one round trip. 20 is a practical default: large enough to usually yield 3 attachment-bearing emails without excessive API calls, small enough to stay fast.
3. For each message ID, fetch the full message using `users.messages.get` with `format=full`. `format=metadata` is insufficient because it returns only headers, not MIME parts; `format=full` is required to inspect the payload tree for attachments.
4. An email qualifies as having an attachment if any MIME part in its payload has a non-empty `filename` field. Inline content (e.g. embedded images with `Content-Disposition: inline`) is excluded — only parts with `Content-Disposition: attachment` or a non-empty `filename` on a non-`text/*` / non-`multipart/*` part are counted.
5. Collect qualifying messages until 3 are found, or the fetched batch is exhausted.
6. Messages are returned in the order Gmail provides them — most recent first by default.

## Output

For each of the (up to 3) matching emails, print:

- **Subject**
- **From**
- **Date**
- **Attachment names** (list of filenames)

Example:

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

If fewer than 3 qualifying emails are found, print however many exist; if none, print `No matching emails with attachments found.`

## Error Handling

- Missing `credentials.json`: print a clear message directing the user to set up a Google Cloud project and download credentials.
- API errors: surface the error message and exit with a non-zero status code.

## Design Decisions

- **Not auto-appending `has:attachment`**: the script does not silently modify the user's query. The attachment filter is applied in code after fetching results, which is visible and predictable. Auto-appending would cause confusion when the user's query already includes it or when debugging sparse results.
- **No pagination**: the script fetches only the first batch of 20 messages. If that batch contains fewer than 3 with attachments, the script stops rather than fetching the next page. This keeps the script simple and fast; users can narrow their query if results are sparse.
- **`format=full` for all fetched messages**: an alternative would be to fetch `format=metadata` first, then re-fetch with `format=full` only for likely matches. That saves quota on large batches but adds complexity. Given the small batch size (20), the simpler single-pass approach is preferred.

## Out of Scope

- Downloading attachment content.
- Support for multiple Gmail accounts simultaneously.
