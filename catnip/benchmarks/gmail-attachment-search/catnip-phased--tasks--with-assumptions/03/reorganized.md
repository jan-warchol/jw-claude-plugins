# Gmail Attachment Search — Spec

## Objective

Build a simple Python CLI script that accepts a Gmail search query from the user and prints the 3 most recent matching emails that contain at least one attachment.

**Motivation**: Quick command-line access to Gmail search results with attachments, without needing a browser.

---

## Requirements

### Must do
- Accept a search query string as a positional CLI argument: `python search_gmail.py "query string"`
- Authenticate with the user's Gmail account using OAuth 2.0 (read-only scope)
- Search Gmail using the provided query, restricted to messages that have attachments
- Return (print to stdout) the 3 most recent matching emails
- For each email, display: subject, sender, date, and attachment filename(s)
- Print errors (auth failures, network errors, no credentials file) to stderr with a clear message; exit non-zero
- Print a human-readable "no results" message if no matching emails are found

### Must not do
- Download or save attachment files to disk
- Modify, delete, or send emails
- Store credentials or tokens in plaintext

### Prerequisites
- Python 3.8 or later
- Dependencies: `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`
- A Google Cloud project with the Gmail API enabled and an OAuth 2.0 Desktop client credentials file (`credentials.json`)

**One-time setup**: Create a Google Cloud project, enable the Gmail API, create an OAuth 2.0 Desktop client, and download `credentials.json` from the Google Cloud Console. After the first browser-based consent, subsequent runs are silent. This assumes the user is technical enough to navigate the Cloud Console; simplifying auth is out of scope.

---

## Solution

### Authentication
Use the **Gmail API** (REST) via `google-api-python-client` with OAuth 2.0, scope `https://www.googleapis.com/auth/gmail.readonly`.

- `credentials.json` path: default `./credentials.json`; overridable via `--credentials <path>` flag or the `GMAIL_CREDENTIALS` environment variable (flag takes precedence).
- First run: open browser for user consent; cache the token in `~/.gmail_token.json`.
- Subsequent runs: silently refresh the cached token using the stored refresh token.
- If the token file is missing or the refresh fails, re-trigger the browser flow.

### Query construction
Combine the user's query with `has:attachment` using Gmail's search syntax:

```
<user_query> has:attachment
```

If the user's query already contains `has:attachment`, do not append it again (simple string check before combining).

### Email retrieval
1. Call `users.messages.list` with `q=<combined_query>` and `maxResults=3`; Gmail returns results newest-first by default.
2. For each returned message ID, call `users.messages.get` with `format=metadata` and `metadataHeaders=[From, Subject, Date]` to fetch headers efficiently.
3. Inspect the `payload.parts` tree to collect attachment filenames (parts where `filename` is non-empty and `body.attachmentId` is present).

This totals at most 4 API calls per run — well within Gmail API quotas for personal use.

### Error handling
| Situation | Behavior |
|---|---|
| `credentials.json` not found | Print path + instructions to stderr, exit 1 |
| OAuth consent cancelled | Print "Authentication cancelled." to stderr, exit 1 |
| Network / API error | Print HTTP status + message to stderr, exit 1 |
| No matching emails | Print "No emails found matching: <query>" to stdout, exit 0 |

### Output
Print a numbered list to stdout:

```
1. Subject: <subject>
   From:    <sender>
   Date:    <date>
   Attachments: <file1.pdf>, <file2.png>

2. ...
```

If fewer than 3 messages match, print however many are found.

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
- Packaging as an installable CLI tool (pip-installable entry point)

---

## Uncertainty

- **"Returns" definition**: Interpreted as printing to stdout. If the script is meant to be imported as a library returning data structures, the interface changes significantly.
- **Result ordering**: Gmail API's `messages.list` returns newest-first by default; the spec relies on this undocumented behavior. It has been consistent in practice, but Google does not formally guarantee the ordering.
