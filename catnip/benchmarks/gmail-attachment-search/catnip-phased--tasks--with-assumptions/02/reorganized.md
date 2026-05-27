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

### Dependencies

- `google-api-python-client`
- `google-auth-oauthlib`
- `google-auth-httplib2`

Standard library only beyond these three packages.

### Authentication

Use the **Gmail API** via `google-api-python-client` and `google-auth-oauthlib`. The user provides a `credentials.json` file (downloaded from Google Cloud Console) placed in the same directory as the script. On first run the script performs the OAuth 2.0 installed-app flow, opens a browser for consent, then stores the resulting token in `token.json` (same directory) for future runs.

**OAuth scope:** `https://www.googleapis.com/auth/gmail.readonly` — the narrowest scope that allows search. This ensures the consent screen shows only read access, not full account control.

If `credentials.json` is missing the script exits with a clear message pointing to setup instructions. If the stored token is expired, the library refreshes it automatically; if refresh fails, the user is re-prompted for consent.

**Assumption:** The user can create a Google Cloud project, enable the Gmail API, and download `credentials.json`. This is a one-time setup step.

### Search

Use the `users.messages.list` endpoint. The effective query becomes `<user_query> has:attachment` — this is printed so the user sees exactly what was run. If the user already includes `has:attachment`, the duplicate is harmless in Gmail's query language.

Request `maxResults=10`. Gmail returns messages newest-first by `internalDate` (date received) by default, so "last 3" means the first 3 results. Take those 3 and fetch their details with `messages.get(format=metadata, metadataHeaders=[From, Subject, Date])` — metadata format retrieves headers and part structure only, not the message body, keeping responses small.

Gmail search returns individual messages, not threads. Multiple replies in the same thread can appear as separate results; this is acceptable for a simple script.

HTTP 4xx/5xx errors from the API (quota exceeded, invalid query, etc.) are caught and printed as human-readable messages; the script exits with a non-zero status code.

**Assumption:** `has:attachment` includes inline images. If only named file attachments are wanted, additional MIME-type filtering would be required (see Uncertainty).

### Output

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

If fewer than 3 results: `Found 1 matching email (fewer than 3 available).`  
If zero results: `No emails found matching: "from:boss report has:attachment"`

---

## Alternatives considered

**IMAP instead of Gmail API:** `imaplib` + `email` require no extra packages but need an App Password (deprecated path) and use a different search syntax from Gmail's native query language. Rejected.

**Third-party wrappers (`simplegmail` etc.):** Add a dependency layer over the official client with no meaningful benefit here. Rejected.

---

## Out of scope

- Downloading or reading attachment content.
- Pagination beyond the first page of results.
- Multiple Gmail accounts simultaneously.
- Sending or composing emails.
- Non-Gmail providers.
- A graphical or web interface.
- Packaging as an installable CLI tool.
- Retry logic for transient API failures.

---

## Uncertainty

- **Scope of "returns":** Assumed to mean printing to stdout. A Python data-structure return (library use) would need a different output layer.
- **"Simple" constraint:** The OAuth setup (credentials.json, first-run browser flow) may feel non-trivial despite being unavoidable with the Gmail API.
- **`has:attachment` precision:** Includes inline images. If only named file attachments (PDFs, spreadsheets, etc.) are wanted, client-side filtering on `Content-Disposition: attachment` would be needed.
- **Error handling depth:** Basic error messages assumed sufficient; retry logic and detailed diagnostics are out of scope.
