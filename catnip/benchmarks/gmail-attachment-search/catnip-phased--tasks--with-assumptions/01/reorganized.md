# Gmail Attachment Search Script — Spec

## Objective

A simple command-line Python script that authenticates with Gmail, accepts a search query from the user, and returns the 3 most recent matching emails that contain at least one attachment. Useful for quickly surfacing attachments buried in a busy inbox without opening a browser.

## Requirements

### Behavior
- Accept a search query string as a CLI argument; fall back to an interactive prompt if omitted
- Authenticate with Gmail via OAuth 2.0 using the `gmail.readonly` scope
- Search the user's Gmail inbox using the provided query, automatically adding `has:attachment` if not already present
- Return the last (most recent) 3 matching emails that have at least one attachment
- For each result, display: subject, sender, date, and attachment filename(s)
- Cache the OAuth token in `token.json` in the current working directory so re-authentication is not required on subsequent runs
- Handle graceful degradation when fewer than 3 matches are found, noting the actual count

### Constraints
- Read-only: no modifying, deleting, sending, or writing emails; no write scopes requested
- No storing email body content or attachment data on disk
- No support for multiple accounts, GUI, pagination beyond 3 results, or reply/forward/label/delete operations

### Error handling
- Print a clear, actionable message if `credentials.json` is missing (include a pointer to the Google Cloud Console setup step)
- Exit with a non-zero code on API errors (quota exceeded, network failure, invalid credentials)
- On result exhaustion with fewer than 3 matches, report what was found rather than failing silently

## Solution

### Authentication

Use the Gmail API via `google-api-python-client` and `google-auth-oauthlib`. On first run, the user completes an OAuth 2.0 browser flow; the token is saved to `token.json` in the working directory and reused on subsequent runs. Scope: `https://www.googleapis.com/auth/gmail.readonly`.

**Assumption:** The user is willing to set up a Google Cloud project and download `credentials.json`. This one-time setup is required for personal Gmail API access.

### Search & filtering

1. If the user's query does not contain `has:attachment`, append it automatically and print a note: `(added has:attachment to query)`.
2. Call `gmail.users().messages().list(userId="me", q=<query>, maxResults=10)` to get an initial batch of message IDs, sorted most-recent-first by default.
3. For each message ID, call `messages.get(format="full")` to retrieve MIME part structure and extract `filename` fields from parts where `filename` is non-empty.
4. Collect up to 3 results, paginating via `nextPageToken` if needed.

Fetching `format="full"` only for messages actually returned (at most 3) keeps API calls low.

### Output

```
(added has:attachment to query)

[1] Subject: Invoice March 2026
    From:    billing@example.com
    Date:    Wed, 12 Mar 2026 10:34:00 +0000
    Files:   invoice-march.pdf

[2] Subject: Project assets
    From:    designer@example.com
    Date:    Mon, 10 Mar 2026 08:12:00 +0000
    Files:   logo.png, banner.svg
```

### Dependencies

- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

### Alternatives considered

- **Gmail IMAP via `imaplib`**: OAuth over IMAP is more complex to set up, less well-documented, and lacks Gmail's rich query syntax.
- **`simplegmail` third-party library**: Simpler API surface, but adds an opaque dependency and is less actively maintained.

### Open questions

- **`format="full"` call volume**: The list endpoint may return messages that pass the `has:attachment` filter but have no accessible filenames (e.g. inline images only). More than 3 `messages.get` calls may be needed before finding 3 results, with no hard upper bound.
- **Inline images vs true attachments**: Gmail's `has:attachment` includes inline images. Should the script filter to only `Content-Disposition: attachment` parts? Defaulting to all named MIME parts is simpler and probably what users expect, but worth confirming.
