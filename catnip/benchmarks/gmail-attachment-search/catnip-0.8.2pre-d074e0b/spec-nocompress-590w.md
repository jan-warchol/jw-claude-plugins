# Gmail Attachment Search Script — Spec

## Goal

Provide a quick command-line tool to find recent Gmail messages that match an arbitrary search
query and have attachments, then display the attachments' metadata. Motivated by the common need
to locate files received via email without manually browsing Gmail's UI.

## Requirements

- Accepts a single Gmail search query string as a CLI argument (same syntax Gmail's search bar
  accepts, e.g. `from:boss subject:report`).
- Searches the user's Gmail account and finds the **3 most recent** messages that:
  - match the query, AND
  - contain at least one attachment.
- For each matching message, prints to stdout:
  - Subject line
  - Sender (`From` header)
  - Received date
  - For each attachment: filename, size (human-readable), MIME type
- If fewer than 3 messages match, prints however many exist (0 is valid; prints a clear "no
  results" message).
- Exits with a non-zero status code on errors (auth failure, network error, API quota exceeded).

**Out of scope:**

- Downloading or saving attachments.
- Pagination beyond the first page of API results (fetching far more than 3 results to find
  matches is acceptable).
- Sending, modifying, or deleting messages.
- OAuth token management UI — a one-time browser login is acceptable.

## Solution

### Authentication

Use the **Google Gmail API** with OAuth 2.0 (`google-auth-oauthlib` + `google-api-python-client`).

- Requires a `credentials.json` from a Google Cloud project (user must obtain this once).
- On first run, opens a browser for the OAuth consent flow and saves a `token.json` locally for
  subsequent runs.
- Scope: `https://www.googleapis.com/auth/gmail.readonly`.

### Search approach

1. Call `users.messages.list` with the user's query. Gmail's API only supports filtering by query,
   not by "has attachment" natively in all cases — use `has:attachment` appended to the user's
   query (Gmail search supports this natively).
2. Fetch message details (`users.messages.get` with `format=metadata`) for the first results until
   3 qualifying messages are collected. Qualifying = payload contains at least one part with a
   `filename` field set.
3. Extract attachment metadata from the message payload parts (no need to call
   `users.messages.attachments.get` since we only need metadata, not content).

### Output format

Plain text, one block per message, separated by blank lines:

```
Date:    2026-05-30
From:    Alice <alice@example.com>
Subject: Q1 Report

  report.pdf   1.2 MB   application/pdf
  notes.docx   45 KB    application/vnd.openxmlformats...
```

### Dependencies

- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

All installable via pip; no other runtime dependencies.

### Key design choices

- Append `has:attachment` to the query automatically rather than requiring the user to include it,
  since it is always implied by the script's purpose.
- Metadata-only fetch (`format=metadata`) avoids downloading full message bodies, keeping the
  script fast.
- `token.json` stored in the working directory (or alongside the script); location can be a
  hardcoded constant easy to change.

## Unknowns

- **Credentials setup friction**: Users must create a Google Cloud project and download
  `credentials.json`. This is the dominant UX cost and is not automated by the script. The script
  should print a clear error (with a pointer to docs) if `credentials.json` is missing.
- **Attachment detection edge cases**: Inline images embedded via `Content-Disposition: inline`
  may or may not be desirable to surface. Assumption: only parts with a non-empty `filename` are
  shown; inline images without filenames are excluded.
- **API quota**: Gmail API has per-user quotas. Not expected to be an issue for interactive use,
  but worth noting for any future automation.
- **Size field availability**: Attachment `size` comes from the `body.size` field in the message
  part; this reflects encoded size, which may differ slightly from the actual file size.
