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

### Dependencies
- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

### Authentication and setup
The user must have a Google Cloud project with the Gmail API enabled and a `credentials.json` file downloaded from the Google Cloud Console. This is a manual prerequisite; the script fails with a descriptive error if the file is absent.

On first run, the script opens a browser for the user to grant access (scope: `https://www.googleapis.com/auth/gmail.readonly`) and stores the resulting token in `token.json` (same directory as the script) for reuse. If the token is revoked, the user must delete `token.json` to re-authenticate.

### CLI interface
Use `argparse` with a single positional argument `query`. Multi-word queries must be quoted using standard shell quoting. Example:

```
python gmail_search.py "invoice from:supplier@example.com"
```

If `query` is omitted, fall back to `input("Search query: ")`.

### Search and filtering
Call `users.messages.list` with the user-supplied query string. Gmail's search syntax is passed through directly (e.g. `from:boss@example.com`, `has:attachment project report`). Results are returned newest-first by Gmail's internal date order.

Including `has:attachment` in the query is recommended (and can be documented as a tip) to pre-filter on the server, reducing API calls. The script still verifies attachments client-side to handle edge cases where Gmail marks inline images as attachments but they carry no meaningful filename.

For each candidate message, call `users.messages.get` with `format=metadata` and walk the `parts` tree **recursively** (Gmail nests parts in multipart/mixed and multipart/alternative messages), collecting parts where `filename` is non-empty. Fetch results page by page and stop once 3 qualifying messages are found.

### Output
```
[1] Subject: <subject>
    From:    <sender>
    Date:    <date>
    Files:   <filename1>, <filename2>, …

[2] …

Found 3 result(s).
```

If fewer than 3: `Found N result(s) (fewer than 3 matched).`
If zero: `No emails matching "<query>" with attachments were found.`

---

## Alternative solutions considered

- **IMAP (imaplib)**: Avoids Google API setup, but requires "less secure app access" or app passwords, provides weaker search, and MIME attachment parsing is more complex.
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

## Known limitations

- **Rate limiting**: Iterating through many pages to find 3 messages with attachments could hit Gmail API quotas on accounts with very large result sets. No retry logic is planned; acceptable for a simple script.
