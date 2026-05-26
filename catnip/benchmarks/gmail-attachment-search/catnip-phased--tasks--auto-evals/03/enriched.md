# Gmail Attachment Search Script — Spec

## Overview

A command-line Python script that accepts a Gmail search query from the user and returns the three most recent matching emails that contain at least one attachment. For each result, the script prints a summary of the email and lists its attachment filenames.

## Authentication

- Uses the Gmail API via `google-auth` and `google-api-python-client`.
- OAuth 2.0 flow with a `credentials.json` file (downloaded from Google Cloud Console).
- On first run, opens a browser for consent; stores the resulting token in `token.json` (in the working directory) for subsequent runs.
- Required OAuth scope: `https://www.googleapis.com/auth/gmail.readonly`.
- **Assumption**: the user has a Google Cloud project with the Gmail API enabled and has downloaded `credentials.json`. Setup is a prerequisite; the script does not automate it.
- **Assumption**: the machine running the script has a browser available for the initial OAuth consent flow.

## Input

- **Search query**: provided as a command-line argument (required).
  - Example: `python search_gmail.py "invoice from:accounting@example.com"`
  - The query uses Gmail's standard search syntax.
- The script does **not** automatically append `has:attachment` to the query. The user controls the full query string. This keeps behavior predictable: the script filters for attachments itself after fetching results, so adding `has:attachment` silently would cause confusion when the user's query already includes it or when debugging unexpected empty results.

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

## Dependencies

- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

Listed in `requirements.txt`.

## Error Handling

- Missing `credentials.json`: print a clear message directing the user to set up a Google Cloud project and download credentials.
- Expired/invalid token: the OAuth library automatically attempts a refresh; if refresh fails, the script re-runs the browser consent flow.
- API errors: surface the error message and exit with a non-zero status code.
- No results found: print a friendly `No matching emails with attachments found.` message.

## Trade-offs and Rejected Alternatives

- **No pagination**: the script fetches only the first batch of 20 messages. If that batch contains fewer than 3 with attachments, the script stops rather than fetching the next page. This keeps the script simple and fast; users can narrow their query if results are sparse.
- **`format=full` for all fetched messages**: an alternative would be to fetch `format=metadata` first to count candidates cheaply, then re-fetch with `format=full` only for likely matches. That would save quota on large batches but adds complexity. Given the small batch size (20), the simpler single-pass approach is preferred.
- **Not auto-appending `has:attachment`**: doing so would make the query opaque and harder to debug. The filtering happens in code, which is visible.

## Out of Scope

- Downloading attachment content.
- Paginating beyond the initial 20-message fetch batch.
- Support for multiple Gmail accounts simultaneously.
