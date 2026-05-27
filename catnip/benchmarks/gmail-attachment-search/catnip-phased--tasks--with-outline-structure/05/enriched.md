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

**Authentication:** Use the Gmail API via `google-api-python-client` + `google-auth-oauthlib`. Request only the `gmail.readonly` scope. On first run, the OAuth flow opens a browser for the user to authorize the app; credentials are cached in `token.json` in the working directory for subsequent runs. The script reads `credentials.json` (OAuth 2.0 desktop client) from the same working directory.

**Search:** Call `users.messages.list` with the effective query `<user_query> has:attachment` (deduplicate if the user already included `has:attachment`). Request up to the first page of results (default 100); Gmail returns newest first by default.

**Fetching details:** Take the first 3 message IDs. For each, call `users.messages.get` with `format=metadata` and `metadataHeaders=[Subject, From, Date]`. Walk `payload.parts` recursively to collect filenames from parts where `filename` is non-empty and `body.attachmentId` is set.

**Output:** Print the numbered summary to stdout. If 0 results are found, print `No matching emails with attachments found.`

**Dependencies:**
- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

**Credentials setup:** The user must create a Google Cloud project, enable the Gmail API, and download `credentials.json` (OAuth 2.0 desktop client) into the script's working directory.

---

## Alternative solutions considered

- **`imaplib` / `IMAPClient`:** Standard IMAP access would avoid the Google API SDK but requires enabling App Passwords and uses a different search syntax. Gmail API is the recommended modern approach.
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

- **`has:attachment` deduplication:** Checking whether the user query already contains `has:attachment` via a simple string check is sufficient; double-including it is harmless but untidy.
- **Attachment detection in nested MIME parts:** Some emails have deeply nested `multipart` structures; a recursive walk of `payload.parts` is needed rather than only inspecting the top level.
- **Token refresh / expiry:** The cached `token.json` approach handles refresh automatically via the library, but the first-run browser pop-up may be surprising in headless environments — worth documenting in the README.
- **API quota:** `users.messages.get` is called up to 3 times per run; this is well within Gmail API's free quota (1 billion units/day) and not a practical concern.
- **`credentials.json` path:** Hardcoding to the working directory is simple but may be inconvenient; an env var or CLI flag (`--credentials`) could override it — deferred as out of scope unless requested.
