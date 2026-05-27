# Gmail Attachment Search Script — Spec

## Objective

A simple command-line Python script that authenticates with Gmail, accepts a search query from the user, and returns the 3 most recent matching emails that contain at least one attachment. Useful for quickly surfacing attachments buried in a busy inbox without opening a browser.

## Requirements

**Must do:**
- Accept a search query string from the user (CLI argument or stdin prompt)
- Authenticate with Gmail via OAuth 2.0 (Google API)
- Search the user's Gmail inbox using the provided query
- Filter results to only emails that have at least one attachment
- Return the last (most recent) 3 such emails
- For each result, display: subject, sender, date, and attachment filename(s)

**Must not:**
- Modify, delete, or send any emails
- Store email body content or attachment data on disk
- Require re-authentication on each run (credentials should be cached)

## Solution

### Authentication

Use the [Gmail API](https://developers.google.com/gmail/api) via the `google-api-python-client` and `google-auth-oauthlib` libraries. On first run, the user completes an OAuth 2.0 browser flow; the resulting token is saved to a local `token.json` file and reused on subsequent runs.

**Assumption:** The user is willing to set up a Google Cloud project and download `credentials.json` (OAuth client secrets). This is the standard approach for personal Gmail API access and requires a one-time setup.

### Search & filtering

1. Call `gmail.users().messages().list()` with the user's query string. Gmail's native query syntax is supported (e.g. `from:alice`, `subject:invoice`, `has:attachment`).
2. Fetch message metadata (headers + part structure) for each result using `format=metadata` with `metadataHeaders=["From","Subject","Date"]` plus a `format=full` check for `filename` in MIME parts — or use `has:attachment` appended to the query as a first pass, then confirm attachment presence in the message payload.
3. Collect results until 3 matching emails are found or the result set is exhausted (handling pagination via `nextPageToken`).

**Assumption:** Appending `has:attachment` to the user query is acceptable if the user didn't already include it — the script will do so automatically to avoid fetching irrelevant messages. This will be noted in output.

### Output

Print to stdout in a human-readable format, one email per block:

```
[1] Subject: Invoice March 2026
    From: billing@example.com
    Date: Wed, 12 Mar 2026 10:34:00 +0000
    Attachments: invoice-march.pdf

[2] ...
```

### Dependencies

- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

## Alternative solutions considered

- **Gmail IMAP via `imaplib`**: No extra OAuth library needed, but IMAP with OAuth is more complex to set up, less well-documented, and lacks the rich query syntax of the Gmail API.
- **`simplegmail` third-party library**: Simpler API surface, but adds an opaque dependency and is less actively maintained.

## Out of scope

- Downloading or saving attachments to disk
- Searching across multiple Gmail accounts
- GUI or web interface
- Pagination / retrieving more than 3 results
- Any write operations (reply, forward, label, delete)

## Uncertainty

- **`credentials.json` UX**: The setup instructions for obtaining credentials from Google Cloud Console are non-trivial. The spec assumes the user is technical enough to follow them, but the script should print a clear error if the file is missing.
- **Query modification**: Automatically appending `has:attachment` may surprise users who intended a different filter; should the script warn or just transparently apply it?
- **Token storage location**: Should `token.json` go in the current working directory, the user's home directory, or a config dir like `~/.config/gmail-search/`? The choice affects portability.
- **Result count when fewer than 3 matches exist**: Script should degrade gracefully and note how many were found.
