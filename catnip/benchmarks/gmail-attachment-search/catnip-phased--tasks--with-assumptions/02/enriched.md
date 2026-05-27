# Gmail Attachment Search — Spec

## Objective

Build a Python CLI script that accepts a Gmail search query from the user, searches the user's Gmail inbox, and prints the three most recent emails that match the query **and** contain at least one attachment.

Use case: quickly surface recent emails with files attached without opening the Gmail web UI or writing custom API calls manually.

---

## Requirements

**Must do:**
- Accept a search query string as a command-line argument (e.g., `python search.py "from:boss report"`).
- Authenticate with Gmail on behalf of the user via OAuth 2.0, requesting only read-only access.
- Search the user's Gmail mailbox using the provided query.
- Filter results to only emails that have at least one attachment.
- Return (print) the three most recent such emails, ordered by received date descending.
- For each result, display: received date (YYYY-MM-DD), sender, subject, and attachment filenames.
- Persist OAuth tokens locally so re-authentication is not required on every run.
- Print a clear message when fewer than 3 (including zero) matching emails are found.

**Must not do:**
- Download or save attachment files to disk (search and list only).
- Modify, delete, send, or otherwise mutate any email data.
- Expose OAuth client secrets or tokens in output.
- Request OAuth scopes beyond what is necessary for read-only search.

---

## Solution

### Authentication

Use the **Gmail API** via `google-api-python-client` and `google-auth-oauthlib`. The user provides a `credentials.json` file (downloaded from Google Cloud Console) placed in the same directory as the script. On first run the script performs the OAuth 2.0 installed-app flow, opens a browser for consent, then stores the resulting token in `token.json` (same directory) for future runs.

**OAuth scope:** `https://www.googleapis.com/auth/gmail.readonly` — the narrowest scope that allows search. This is explicit so the consent screen shows only read access, not full account control.

**Assumption:** The user can create a Google Cloud project, enable the Gmail API, and download `credentials.json`. This is a one-time setup step.

**Error cases:** If `credentials.json` is missing the script exits with a clear message pointing to the setup instructions. If the stored token is expired, the library refreshes it automatically using the refresh token; if refresh fails, the user is re-prompted for consent.

### Search

Use the Gmail API's `users.messages.list` endpoint with the user's query string. Gmail's native search syntax is used directly (same syntax as the Gmail web search bar).

**Filtering for attachments:** The query becomes `<user_query> has:attachment`. This is printed so the user sees the exact query run. If the user already includes `has:attachment`, the duplicate is harmless in Gmail's query language.

**Note on threads vs. messages:** Gmail search returns individual messages, not threads. If multiple replies in the same thread each have attachments, they appear as separate results. This is consistent with Gmail API semantics and acceptable for a simple script.

**Assumption:** Combining the user query with `has:attachment` produces correct results. `has:attachment` includes inline images; if only named file attachments are needed, additional MIME-type filtering would be required (left as a noted uncertainty).

### Pagination and result count

Request up to 10 messages from the API (`maxResults=10`). Gmail returns results newest-first by `internalDate` (the date the message was received/created) by default — "last 3" means the 3 with the highest `internalDate`. Take the first 3 from the response.

For the common case: one `messages.list` call + up to 3 `messages.get` calls. Each `messages.get` uses `format=metadata` with `metadataHeaders=[From, Subject, Date]` — this fetches only headers and part structure, not the message body, keeping responses small and fast.

**API errors:** HTTP 4xx/5xx responses from the API are caught and printed as human-readable messages (e.g., quota exceeded, invalid query syntax). The script exits with a non-zero status code on error.

### Output format

Print to stdout, one email per block:

```
Query: "from:boss report has:attachment"

[1] 2024-03-15  From: boss@example.com
    Subject: Q1 Report
    Attachments: report.pdf, summary.xlsx

[2] 2024-02-28  From: boss@example.com
    Subject: February Update
    Attachments: feb_update.pptx

[3] ...
```

If fewer than 3 matching emails exist:
```
Found 1 matching email (fewer than 3 available).

[1] ...
```

If zero results:
```
No emails found matching: "from:boss report has:attachment"
```

### Dependencies

- `google-api-python-client`
- `google-auth-oauthlib`
- `google-auth-httplib2`

Standard library only beyond these three packages.

---

## Alternative solutions considered

**IMAP instead of Gmail API**
Python's `imaplib` + `email` stdlib modules work with Gmail over IMAP, no extra packages required. However, IMAP requires an App Password (less secure, deprecated path), and the search query syntax differs from Gmail's native syntax. Rejected in favour of the official API.

**`simplegmail` or other wrappers**
Third-party wrappers add an extra dependency layer over the official client without meaningful benefit for this use case. Rejected.

---

## Out of scope

- Downloading or reading attachment content.
- Pagination beyond the first page of results (unlikely to matter for fetching 3 emails).
- Support for multiple Gmail accounts simultaneously.
- Sending or composing emails.
- Non-Gmail providers (IMAP generic support).
- A graphical or web interface.
- Packaging as an installable CLI tool.
- Retry logic for transient API failures.

---

## Uncertainty

- **Scope of "returns":** Assumed to mean printing summary information to stdout. If a Python data-structure return (for use as a library function) is needed, the output layer would be different.
- **"Simple" constraint:** The OAuth setup (credentials.json, first-run browser flow) is unavoidable with the Gmail API and may feel non-trivial. IMAP with an App Password is simpler to configure but has other trade-offs.
- **`has:attachment` precision:** Includes inline images. If only named file attachments (PDFs, spreadsheets, etc.) are wanted, client-side MIME-type filtering on `Content-Disposition: attachment` would be needed.
- **Error handling depth:** Basic error messages are assumed sufficient. Retry logic and detailed diagnostics are out of scope.
