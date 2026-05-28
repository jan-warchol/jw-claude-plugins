# Gmail Attachment Search — Spec

## Objective

Build a simple Python CLI script that accepts a Gmail search query from the user and prints the 3 most recent matching emails that contain at least one attachment.

**Motivation**: Quick command-line access to Gmail search results with attachments, without needing a browser.

---

## Requirements

### Must do
- Accept a search query string (as a CLI argument or via stdin prompt)
- Authenticate with the user's Gmail account
- Search Gmail using the provided query, restricted to messages that have attachments
- Return (print to stdout) the 3 most recent matching emails
- For each email, display: subject, sender, date, and attachment filename(s)

### Must not do
- Download or save attachment files to disk
- Modify, delete, or send emails
- Store credentials in plaintext

---

## Solution

### Authentication
Use the **Gmail API** (REST) via `google-api-python-client` with OAuth 2.0.

- First run: open browser for user consent; cache the token in `~/.gmail_token.json`
- Subsequent runs: silently refresh the cached token

Requires the user to provide `credentials.json` (downloaded from Google Cloud Console) in the working directory or a configured path.

### Query construction
Combine the user's query with `has:attachment` using Gmail's search syntax:

```
<user_query> has:attachment
```

This ensures only messages with attachments are considered without needing a post-filter pass.

### Email retrieval
1. Call `users.messages.list` with `q=<combined_query>` and `maxResults=3`; Gmail returns results newest-first by default.
2. For each returned message ID, call `users.messages.get` with `format=metadata` and `metadataHeaders=[From, Subject, Date]` to fetch headers efficiently.
3. Inspect the `payload.parts` tree to collect attachment filenames (parts where `filename` is non-empty and `body.attachmentId` is present).

### Output
Print a numbered list to stdout:

```
1. Subject: <subject>
   From:    <sender>
   Date:    <date>
   Attachments: <file1.pdf>, <file2.png>

2. ...
```

If fewer than 3 messages match, print however many are found (or a "no results" message).

### Dependencies
- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

---

## Alternative solutions considered

| Approach | Why not chosen |
|---|---|
| IMAP (`imaplib`) | Requires enabling "less secure app access" or an app password; Gmail API is the officially supported path |
| `simplegmail` / third-party wrapper | Adds a dependency with less control; thin wrapper over the same API |
| `gmail` CLI tool (Go) | Not Python; outside scope |

---

## Out of scope

- Downloading or previewing attachment content
- Pagination beyond the first 3 results
- Support for multiple Gmail accounts simultaneously
- GUI or interactive TUI
- Filtering by attachment type, size, or name

---

## Uncertainty

- **OAuth setup friction**: The spec assumes the user can create a Google Cloud project and download `credentials.json`. If the target audience is non-technical, a simpler auth path (e.g., service account or a pre-registered app) may be needed.
- **`credentials.json` path**: Should it be configurable via a flag or environment variable, or hardcoded to the working directory? The spec currently assumes working directory.
- **"Returns" definition**: Interpreted as printing to stdout. If the script is meant to be imported as a library and return data structures, the interface changes significantly.
- **Result ordering**: Gmail API's `messages.list` returns newest-first by default; the spec relies on this. If the user wants a different sort order, an explicit `orderBy` would be needed (the API does not directly support `orderBy` for messages — sorting is inherent to the query).
- **Quota**: Gmail API has per-user read quotas; the script makes up to 4 API calls (1 list + 3 get) per run, well within limits for personal use.
