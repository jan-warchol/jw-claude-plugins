# Spec: Gmail Search with Attachment Filter

## Objective

Python CLI script: authenticate with Gmail, run a user-provided search query, return the 3 most recent matching emails that have attachments. Use case: ad-hoc retrieval without the Gmail web UI.

---

## Requirements

**Must do:**
- Accept the query as a positional CLI argument (e.g., `python search_gmail.py "invoice from:acme"`)
- Authenticate via OAuth 2.0 (`gmail.readonly` scope)
- Search Gmail with the query filtered to messages with attachments
- Return up to 3 most recent matches; degrade gracefully if fewer exist
- Per result: display subject, sender, date, attachment filename(s)
- Exit non-zero with a readable message on auth or API errors

**Must not:** download attachments, modify/delete/send emails, run as a daemon.

**Example output:**
```
[1] Subject: Q1 Invoice
    From:    billing@acme.com
    Date:    Mon, 12 May 2025 09:14:32 +0000
    Files:   invoice_q1.pdf, terms.docx
```

---

## Solution

**Authentication:** `google-api-python-client` + `google-auth-oauthlib`, `gmail.readonly` scope. First run opens a browser for authorization; token cached in `token.json` (working directory).

**Search:** `users.messages.list` with query `<user_query> has:attachment` (deduplicate if already present). Gmail returns newest-first; fetch first page (default 100).

**Fetching details:** For each of the first 3 IDs, call `users.messages.get` with `format=metadata`, `metadataHeaders=[Subject, From, Date]`. Recursively walk `payload.parts` to collect filenames where `filename` is non-empty and `body.attachmentId` is set.

**Output:** Numbered summary to stdout; print `No matching emails with attachments found.` if 0 results.

### Setup & dependencies

Dependencies: `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`.

Credentials: create a Google Cloud project, enable the Gmail API, download `credentials.json` (OAuth 2.0 desktop client) to the working directory.

---

## Alternatives considered

- **`imaplib`/`IMAPClient`:** requires App Passwords, different search syntax — Gmail API is preferred.
- **`simplegmail`/wrappers:** simpler surface but opaque dependency; official SDK is sufficient.

---

## Out of scope

Downloading attachments · pagination past page 1 · configurable result count · non-Gmail/IMAP · GUI · batch/scheduled execution

---

## Uncertainty

- **Headless environments:** first-run OAuth browser pop-up should be documented in the README.
- **`credentials.json` path:** hardcoded to working directory; `--credentials` flag deferred unless requested.
