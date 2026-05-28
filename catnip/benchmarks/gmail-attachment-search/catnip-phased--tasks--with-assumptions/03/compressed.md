# Gmail Attachment Search — Spec

## Objective

Python CLI script that searches Gmail with a user-provided query and prints the 3 most recent matching emails that have attachments. Avoids needing a browser for quick attachment lookups.

---

## Requirements

### Must do
- Accept query as a positional CLI argument: `python search_gmail.py "query string"`
- Authenticate via OAuth 2.0 (read-only scope)
- Restrict results to messages with attachments
- Print the 3 most recent matches (subject, sender, date, attachment filenames) to stdout
- Print errors to stderr, exit non-zero; print "no results" message when nothing matches

### Must not do
- Download or save attachments
- Modify, delete, or send emails
- Store credentials or tokens in plaintext

### Prerequisites
- Python 3.8+; `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`
- `credentials.json` from Google Cloud Console (Gmail API enabled, OAuth 2.0 Desktop client)

**One-time setup**: Create a Google Cloud project, enable the Gmail API, create a Desktop OAuth client, download `credentials.json`. First run opens a browser for consent; subsequent runs are silent. Assumes a technical user comfortable with the Cloud Console.

---

## Solution

### Authentication
Gmail API via `google-api-python-client`, scope `https://www.googleapis.com/auth/gmail.readonly`.

- `credentials.json`: defaults to `./credentials.json`; overridable via `--credentials <path>` or `GMAIL_CREDENTIALS` env var (flag takes precedence).
- Token cached in `~/.gmail_token.json`; silently refreshed on subsequent runs. Missing or invalid token re-triggers the browser flow.

### Query construction
Append `has:attachment` to the user's query (skip if already present):
```
<user_query> has:attachment
```

### Email retrieval
1. `users.messages.list` with `q=<combined_query>`, `maxResults=3` — returns newest-first.
2. For each message ID, `users.messages.get` with `format=metadata`, `metadataHeaders=[From, Subject, Date]`.
3. Collect attachment filenames from `payload.parts` (parts where `filename` is non-empty and `body.attachmentId` is set).

At most 4 API calls per run — well within personal-use quotas.

### Error handling
| Situation | Behavior |
|---|---|
| `credentials.json` not found | Path + instructions → stderr, exit 1 |
| OAuth consent cancelled | "Authentication cancelled." → stderr, exit 1 |
| Network / API error | HTTP status + message → stderr, exit 1 |
| No matching emails | "No emails found matching: <query>" → stdout, exit 0 |

### Output
```
1. Subject: <subject>
   From:    <sender>
   Date:    <date>
   Attachments: <file1.pdf>, <file2.png>

2. ...
```
Prints fewer than 3 results if fewer match.

---

## Alternative solutions considered

| Approach | Why not chosen |
|---|---|
| IMAP (`imaplib`) | Needs "less secure app access" or app password; API is the supported path |
| `simplegmail` / third-party wrapper | Extra dependency, thin wrapper over the same API |
| `gmail` CLI (Go) | Not Python |

---

## Out of scope
- Downloading/previewing attachment content
- Pagination beyond 3 results
- Multiple accounts
- GUI / TUI
- Filtering by attachment type, size, or name
- pip-installable packaging

---

## Uncertainty

- **"Returns" meaning**: Spec assumes stdout output. If library-style return values are needed, the interface changes significantly.
- **Result ordering**: `messages.list` returns newest-first in practice, but Google does not formally guarantee this order.
