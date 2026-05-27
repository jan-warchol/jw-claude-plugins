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
- Return the 3 most recent such emails (messages, not threads).
- For each match, print: sender, subject, date received, and the filename(s) of attachments.
- If fewer than 3 matching emails are found, print however many exist with a trailing note (e.g. `Found 1 of 3 requested results.`).
- If no matching emails are found, print a clear message and exit 0.
- On auth failure or unrecoverable API error, print an error message to stderr and exit with a non-zero code.

### Must not do
- Modify, delete, or send emails.
- Store or cache credentials in plain text.

---

## Solution

### Setup
The user must create a Google Cloud project, enable the Gmail API, create OAuth 2.0 desktop credentials, and download the resulting `credentials.json`. The script should print a brief pointer to the setup guide if `credentials.json` is not found.

Dependencies:
- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

### Authentication
Use the Gmail API via `google-api-python-client` and `google-auth-oauthlib`. On first run, an OAuth 2.0 consent flow opens in the browser; the resulting token is saved to `token.json` for subsequent runs. Credentials are read from `credentials.json` in the working directory (configurable via `--credentials` flag). `google-auth-oauthlib` handles token refresh automatically; if the token is revoked, the script deletes the stale `token.json` and re-triggers the consent flow.

### Search & filtering
1. Append `has:attachment` to the user's query before calling `users.messages.list`, so the API pre-filters results and reduces unnecessary `messages.get` calls. (Fetching all results and checking parts client-side would waste API quota.)
2. Set `maxResults=20` as an upper bound. If the first page yields fewer than 3 hits, stop — do not paginate (see Out of scope).
3. For each message ID, call `users.messages.get` with `format=metadata` and recursively traverse all MIME `parts` (including nested multipart trees) to collect parts where `filename` is non-empty. Include all named parts — inline images sent as named MIME parts will appear alongside true attachments; this is acceptable and avoids a fragile heuristic.
4. Operate on individual messages, not threads — if a thread contains multiple messages with attachments, each counts as a separate result.

### Output
Plain-text to stdout, one email block per result:

```
[1] From: sender@example.com
    Subject: Invoice Q1
    Date: Mon, 12 May 2026 09:14:00 +0000
    Attachments: invoice_q1.pdf

[2] ...

Found 2 of 3 requested results.   ← only printed when < 3 found
```

---

## Alternative solutions considered

- **IMAP (`imaplib`)** — standard library, no extra install, but IMAP access must be enabled manually in Gmail settings and is being phased out in favour of the API; OAuth via IMAP is more complex to set up.
- **`simplegmail` / other wrappers** — thinner boilerplate, but add an extra dependency with less official support and less control over pagination/filtering.

---

## Out of scope

- Support for multiple Gmail accounts.
- Automatic pagination beyond the initial `maxResults=20` window.
- Interactive TUI or GUI.
- Packaging as an installable library or pip package.
- Unit/integration test suite.

---

## Uncertainty

- **`maxResults` ceiling**: if the user's query (even with `has:attachment`) returns many results where the first 20 slip past the attachment filter, we may not find 3 hits. Acceptable risk given scope; document as a known limitation.
