# Spec: Gmail Search with Attachment Filter

## Objective

Build a simple Python CLI script that authenticates with Gmail, runs a user-provided search query, and returns the 3 most recent matching emails that have at least one attachment. The primary use case is quick ad-hoc retrieval of attachment-bearing emails without navigating the Gmail web UI.

---

## Requirements

**Must do:**
- Accept a search query string as a positional CLI argument (e.g., `python search_gmail.py "invoice from:acme"`)
- Authenticate with Gmail using OAuth 2.0 with the `gmail.readonly` scope
- Search Gmail using the provided query, additionally filtered to messages with attachments
- Return the 3 most recent matching emails that contain at least one attachment
- For each returned email, display: subject, sender, date, and attachment filename(s)
- Degrade gracefully when fewer than 3 results exist (print however many are found, with a note)
- Exit with a non-zero code and a human-readable message on auth or API errors

**Must not:**
- Download or save attachment content to disk
- Modify, delete, or send any emails
- Require a persistent server or daemon process

**Example output (one result):**
```
[1] Subject: Q1 Invoice
    From:    billing@acme.com
    Date:    Mon, 12 May 2025 09:14:32 +0000
    Files:   invoice_q1.pdf, terms.docx
```

---

## Solution

**Authentication:** Use the Gmail API via `google-api-python-client` + `google-auth-oauthlib` with the `gmail.readonly` scope. On first run, the OAuth flow opens a browser; the resulting token is cached in `token.json` in the working directory for subsequent runs.

**Search:** Call `users.messages.list` with the effective query `<user_query> has:attachment`, deduplicating `has:attachment` if the user already included it. Gmail returns results newest-first by default; request up to the first page (default 100).

**Fetching details:** Take the first 3 message IDs. For each, call `users.messages.get` with `format=metadata` and `metadataHeaders=[Subject, From, Date]`. Walk `payload.parts` recursively to collect filenames from parts where `filename` is non-empty and `body.attachmentId` is set (handles deeply nested `multipart` structures).

**Output:** Print the numbered summary to stdout. If 0 results are found, print `No matching emails with attachments found.`

### Setup & dependencies

**Python dependencies:**
- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

**Credentials:** The user must create a Google Cloud project, enable the Gmail API, and download an OAuth 2.0 desktop-client `credentials.json` into the script's working directory.

---

## Alternative solutions considered

- **`imaplib` / `IMAPClient`:** Standard IMAP access avoids the Google SDK but requires App Passwords and uses a different search syntax. Gmail API is the recommended modern approach.
- **`simplegmail` / third-party wrappers:** Simpler API surface but adds an opaque dependency; the official SDK is straightforward enough for this scope.

---

## Out of scope

- Downloading or saving attachment files
- Pagination beyond the first result page
- Configuring result count (hardcoded to 3)
- Support for non-Gmail accounts or generic IMAP
- A GUI or web interface
- Batch/scheduled execution

---

## Uncertainty

- **Token refresh in headless environments:** The first-run OAuth browser pop-up may be surprising; worth documenting in the README.
- **`credentials.json` path:** Hardcoding to the working directory is simple but may be inconvenient; a `--credentials` CLI flag or env var override is deferred unless requested.
