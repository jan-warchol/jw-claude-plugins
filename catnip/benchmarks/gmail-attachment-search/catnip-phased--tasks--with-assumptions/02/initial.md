# Gmail Attachment Search — Spec

## Objective

Build a Python CLI script that accepts a Gmail search query from the user, searches the user's Gmail inbox, and prints the three most recent emails that match the query **and** contain at least one attachment.

Use case: quickly surface recent emails with files attached without opening the Gmail web UI or writing custom API calls manually.

---

## Requirements

**Must do:**
- Accept a search query string as a command-line argument (e.g., `python search.py "from:boss report"`).
- Authenticate with Gmail on behalf of the user via OAuth 2.0.
- Search the user's Gmail mailbox using the provided query.
- Filter results to only emails that have at least one attachment.
- Return (print) the three most recent such emails.
- For each result, display enough detail to identify the email: date, sender, subject, and attachment filenames.
- Persist OAuth tokens locally so re-authentication is not required on every run.

**Must not do:**
- Download or save attachment files to disk (search and list only).
- Modify, delete, send, or otherwise mutate any email data.
- Expose OAuth client secrets or tokens in output.

---

## Solution

### Authentication

Use the **Gmail API** via `google-api-python-client` and `google-auth-oauthlib`. The user provides a `credentials.json` file (downloaded from Google Cloud Console) on first run. The script performs the OAuth 2.0 installed-app flow, opens a browser for consent, then stores the resulting token in `token.json` for future runs.

**Assumption:** The user can create a Google Cloud project, enable the Gmail API, and download `credentials.json`. This is a one-time setup step.

### Search

Use the Gmail API's `users.messages.list` endpoint with the user's query string. Gmail's native search syntax is used directly (same syntax as the Gmail web search bar), so `has:attachment` does not need to be appended by the script — but see the filtering note below.

**Filtering for attachments:** Two options:
1. Append `has:attachment` to the user's query automatically → simpler, relies on Gmail's server-side filter.
2. Fetch messages and inspect `payload.parts` client-side → slower, more API calls.

Option 1 is chosen. The query becomes `<user_query> has:attachment`. This is transparent and consistent with Gmail behavior. A note is printed so the user knows what query was run.

**Assumption:** Combining the user query with `has:attachment` produces correct results. Edge case: if the user already includes `has:attachment` in their query, the duplicate term is harmless in Gmail's query language.

### Pagination and result count

Request up to 10 results from the API (more than needed to account for any edge cases), sort by recency (Gmail returns results newest-first by default), and take the first 3 that pass validation.

For the common case this means a single API call for the list plus up to 3 `messages.get` calls to fetch headers and part metadata.

### Output format

Print to stdout, one email per block:

```
[1] 2024-03-15  From: boss@example.com
    Subject: Q1 Report
    Attachments: report.pdf, summary.xlsx

[2] ...
```

If fewer than 3 matching emails exist, print however many were found with a note.

### Dependencies

- `google-api-python-client`
- `google-auth-oauthlib`
- `google-auth-httplib2`

Standard library only beyond these three packages.

---

## Alternative solutions considered

**IMAP instead of Gmail API**
Python's `imaplib` + `email` stdlib modules work with Gmail over IMAP, no extra packages required. However, IMAP requires enabling "less secure app access" or an App Password (both deprecated/discouraged by Google), and the search query syntax differs from Gmail's native syntax. Rejected in favour of the official API.

**`simplegmail` or other wrappers**
Third-party wrappers exist but add an extra dependency layer over the official client. The official client library is straightforward enough for this use case.

---

## Out of scope

- Downloading or reading attachment content.
- Pagination beyond the first page of results (unlikely to matter for fetching 3 emails).
- Support for multiple Gmail accounts simultaneously.
- Sending or composing emails.
- Non-Gmail providers (IMAP generic support).
- A graphical or web interface.
- Packaging as an installable CLI tool.

---

## Uncertainty

- **Scope of "returns":** The request says "returns the last 3 matching emails." It is assumed this means printing summary information to stdout. If the intent is to return a Python data structure (for use as a library function), the output layer would be different.
- **"Simple" constraint:** The OAuth setup (credentials.json, first-run browser flow) is unavoidable with the Gmail API and may feel non-trivial. If truly minimal setup is required, IMAP with an App Password is simpler to configure but comes with other trade-offs.
- **`has:attachment` precision:** Gmail's `has:attachment` includes inline images. If the user only wants file attachments (PDFs, spreadsheets, etc.), additional client-side filtering on MIME type or disposition would be needed.
- **Error handling depth:** It is assumed basic error messages (invalid credentials, no results found, API quota exceeded) are sufficient. Retry logic and detailed diagnostics are out of scope for a "simple" script.
