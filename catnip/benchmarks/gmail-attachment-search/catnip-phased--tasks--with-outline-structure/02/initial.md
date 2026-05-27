# Gmail Attachment Search — Spec

## Objective

Build a simple command-line Python script that accepts a search query from the user, queries their Gmail inbox via the Gmail API, and prints the 3 most recent matching emails that contain at least one attachment.

Motivation: quickly surface relevant emails with attachments without opening a browser, useful for automation, scripting pipelines, or personal productivity.

---

## Requirements

### Must do
- Accept a search query string as a CLI argument (or prompt interactively).
- Authenticate with Gmail using OAuth 2.0 (Google API credentials).
- Search the authenticated user's Gmail account using the provided query.
- Filter results to emails that have at least one attachment.
- Return (print) the 3 most recent matching emails with attachments.
- For each result, display: subject, sender, date, and attachment filename(s).

### Must not do
- Download or save attachment files to disk (display metadata only).
- Modify, delete, or send any emails.
- Store or transmit credentials beyond what the OAuth flow requires.

---

## Solution

### Authentication
Use the `google-auth` + `google-auth-oauthlib` libraries with OAuth 2.0.
- On first run, open a browser for the user to grant access; store the resulting token in a local `token.json` file for reuse.
- Required scope: `https://www.googleapis.com/auth/gmail.readonly`.
- The user must provide a `credentials.json` file downloaded from the Google Cloud Console (OAuth 2.0 client credentials).

### Search
Call `users.messages.list` with the user-supplied query string. Gmail's search syntax is used directly (same as the Gmail search bar), so queries like `from:boss@example.com` or `project report` work out of the box.

### Filtering for attachments
For each message returned, call `users.messages.get` with `format=metadata` and check the `parts` tree for any part where `filename` is non-empty. Only keep messages that have at least one such part.

Because `messages.list` returns results newest-first and we want the 3 most recent with attachments, fetch results in pages, check each message for attachments, and stop once 3 qualifying messages are found (to avoid unnecessary API calls).

### Output
Print a human-readable summary for each of the 3 matches:

```
[1] Subject: <subject>
    From:    <sender>
    Date:    <date>
    Files:   <filename1>, <filename2>, …

[2] …
```

### Dependencies
- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

---

## Alternative solutions considered

- **IMAP (imaplib)**: Avoids Google API setup, but requires enabling "less secure app access" or app passwords, provides weaker search capabilities, and parsing MIME attachments is more complex.
- **`simplegmail` / third-party wrappers**: Reduces boilerplate but adds an extra dependency with less transparency; not worth it for a simple script.

---

## Out of scope

- Downloading or saving attachment content.
- Pagination UI / fetching more than the 3 most recent results.
- Support for multiple Gmail accounts simultaneously.
- Non-attachment email fields (body text, labels, thread info).
- GUI or web interface.
- Unit/integration tests.

---

## Uncertainty

- **Attachment detection accuracy**: Gmail's `parts` structure can be nested (multipart/mixed containing multipart/alternative, etc.). A shallow check of top-level parts may miss attachments buried deeper. A recursive walk of the parts tree is safer but slightly more complex — needs a decision on depth.
- **Rate limiting**: For accounts with very large result sets, iterating through many pages to find 3 messages with attachments could hit API quotas. Acceptable for a simple script but worth noting.
- **`credentials.json` distribution**: How the user obtains and places the credentials file is outside the script's control; the script should give a clear error if it's missing.
- **Token refresh**: The `google-auth` library handles token refresh automatically, but if the token is revoked the user must re-authenticate manually by deleting `token.json`.
