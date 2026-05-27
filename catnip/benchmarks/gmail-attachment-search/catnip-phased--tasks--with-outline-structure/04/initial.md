# Gmail Attachment Search — Spec

## Objective

Build a small Python CLI script that accepts a Gmail search query from the user and returns the three most recent matching emails that contain at least one attachment, printing relevant metadata (sender, subject, date, attachment filenames) to stdout.

Motivation: a quick command-line tool for locating attachments in Gmail without opening the web UI, useful for scripting and automation.

---

## Requirements

### Must do
- Accept a search query string as a CLI argument (or prompt for one interactively).
- Authenticate to Gmail via the Gmail API using OAuth 2.0.
- Search the authenticated user's inbox (all mail) using the provided query.
- Filter results to only emails that have at least one attachment.
- Return the 3 most recent such emails.
- For each match, print: sender, subject, date received, and the filename(s) of attachments.

### Must not do
- Download attachment content (filenames only, not file bytes).
- Modify, delete, or send emails.
- Store or cache credentials in plain text.

---

## Solution

### Authentication
Use the **Gmail API** via `google-api-python-client` and `google-auth-oauthlib`. On first run, an OAuth 2.0 consent flow opens in the browser; the resulting token is saved to `token.json` for subsequent runs. Credentials (client ID/secret) are read from a `credentials.json` file the user downloads from Google Cloud Console.

### Search & filtering
1. Call `users.messages.list` with the user's query string and `maxResults` set to a reasonable upper bound (e.g. 20) to handle cases where many results lack attachments.
2. For each returned message ID, call `users.messages.get` with `format=metadata` and fetch the `parts` of the payload to detect attachments (any part where `filename` is non-empty and `mimeType != 'text/*'`).
3. Collect emails that have ≥1 attachment; stop once 3 are found (process in order returned by the API, which is newest-first by default).

### Output
Plain-text to stdout, one email block per result:

```
[1] From: sender@example.com
    Subject: Invoice Q1
    Date: Mon, 12 May 2026 09:14:00 +0000
    Attachments: invoice_q1.pdf
```

### Dependencies
- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

No third-party frameworks beyond the Google client libraries.

---

## Alternative solutions considered

- **IMAP (`imaplib`)** — standard library, no extra install, but IMAP access must be enabled manually in Gmail settings and is being phased out in favour of the API; OAuth via IMAP is more complex to set up.
- **`simplegmail` / other wrappers** — thinner boilerplate, but add an extra dependency with less official support and less control over pagination/filtering.

---

## Out of scope

- Downloading or saving attachment files.
- Support for multiple Gmail accounts.
- Pagination beyond the initial `maxResults` window (e.g. fetching more than 20 candidates).
- Interactive TUI or GUI.
- Packaging as an installable library or pip package.
- Unit/integration test suite.

---

## Uncertainty

- **`maxResults` ceiling**: if the user's query returns many results that are all attachment-free, we may exhaust the first page without finding 3 hits. Decide whether to paginate automatically or document the limitation.
- **Thread vs. message semantics**: Gmail's API returns messages; a thread (conversation) may contain multiple messages. Clarify whether "3 emails" means 3 messages or 3 threads.
- **Attachment detection heuristic**: multipart emails can nest parts arbitrarily; a simple top-level `parts` scan may miss deeply nested attachments. Decide on depth of traversal.
- **`credentials.json` path**: hardcode a conventional default path or make it configurable via CLI flag or env var?
- **Token refresh**: `google-auth-oauthlib` handles refresh automatically, but if the token is revoked the user must re-authenticate. Document expected behaviour.
