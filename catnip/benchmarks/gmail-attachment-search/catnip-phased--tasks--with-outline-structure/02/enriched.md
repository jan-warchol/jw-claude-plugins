# Gmail Attachment Search — Spec

## Objective

Build a simple command-line Python script that accepts a search query from the user, queries their Gmail account via the Gmail API, and prints up to the 3 most recent matching emails that contain at least one attachment (subject, sender, date, and attachment filenames for each).

Motivation: quickly surface relevant emails with attachments without opening a browser, useful for automation, scripting pipelines, or personal productivity.

---

## Requirements

### Must do
- Accept a search query string as a CLI argument; if omitted, prompt interactively.
- Authenticate with Gmail using OAuth 2.0 (Google API credentials).
- Search the authenticated user's Gmail account using the provided query.
- Filter results to emails that have at least one attachment.
- Print up to the 3 most recent matching emails with attachments.
- For each result, display: subject, sender, date, and attachment filename(s).
- If fewer than 3 matching emails with attachments exist, print however many are found and note the total count.
- Exit with a clear, human-readable error message on common failure modes: missing `credentials.json`, authentication failure, network error, or zero results.

### Must not do
- Download or save attachment files to disk (display metadata only).
- Modify, delete, or send any emails.
- Store or transmit credentials beyond what the OAuth flow requires.

---

## Solution

### Prerequisites
The user must have a Google Cloud project with the Gmail API enabled and must download an OAuth 2.0 client credentials file (`credentials.json`) from the Google Cloud Console. This setup is manual and outside the script; the script should fail with a descriptive message if `credentials.json` is absent.

### Authentication
Use `google-auth` + `google-auth-oauthlib` with OAuth 2.0.
- On first run, open a browser for the user to grant access; store the resulting token in `token.json` (same directory as the script) for reuse.
- Required scope: `https://www.googleapis.com/auth/gmail.readonly`.
- If the token is revoked, the user must delete `token.json` and re-authenticate; the script should surface a clear prompt for this.

### CLI interface
Use `argparse` with a single positional argument `query`. Multi-word queries must be quoted by the user (standard shell quoting). Example:

```
python gmail_search.py "invoice from:supplier@example.com"
```

If `query` is omitted, fall back to `input("Search query: ")`.

### Search
Call `users.messages.list` with the user-supplied query string. Gmail's search syntax is passed through directly, so queries like `from:boss@example.com` or `has:attachment project report` work without modification. Results are returned newest-first by Gmail's internal date order.

### Filtering for attachments
For each candidate message, call `users.messages.get` with `format=metadata`. Walk the `parts` tree **recursively** (Gmail nests parts for multipart/mixed and multipart/alternative messages), collecting any part where `filename` is a non-empty string. A message qualifies if at least one such part is found.

Fetch results page by page, evaluate each message, and stop as soon as 3 qualifying messages are found to minimise API calls.

### Output
Print a human-readable summary:

```
[1] Subject: <subject>
    From:    <sender>
    Date:    <date>
    Files:   <filename1>, <filename2>, …

[2] …

Found 3 result(s).
```

If fewer than 3 results are found, print `Found N result(s) (fewer than 3 matched).`
If zero results: `No emails matching "<query>" with attachments were found.`

### Dependencies
- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

---

## Alternative solutions considered

- **IMAP (imaplib)**: Avoids Google API setup, but requires enabling "less secure app access" or app passwords, provides weaker search capabilities, and MIME attachment parsing is more complex.
- **`simplegmail` / third-party wrappers**: Reduces boilerplate but adds a dependency with less transparency; not worth it for a simple script.

---

## Out of scope

- Downloading or saving attachment content.
- Fetching more than the 3 most recent results.
- Support for multiple Gmail accounts simultaneously.
- Non-attachment email fields (body text, labels, thread info).
- GUI or web interface.
- Unit/integration tests.

---

## Uncertainty

- **Rate limiting**: Iterating through many pages to find 3 messages with attachments could hit Gmail API quotas on accounts with very large result sets. Acceptable for a simple script; no retry logic is planned.
- **`has:attachment` vs. client-side filtering**: The Gmail query syntax supports `has:attachment`, which pre-filters on the server and reduces API calls significantly. The script can document this as a recommended query suffix but should still client-side verify attachments to handle edge cases (inline images that Gmail counts as attachments but have no meaningful filename).
