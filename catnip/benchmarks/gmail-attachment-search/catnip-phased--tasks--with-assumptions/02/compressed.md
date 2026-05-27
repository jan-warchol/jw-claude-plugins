# Gmail Attachment Search — Spec

## Objective

Python CLI script: takes a Gmail search query, searches the user's mailbox, and prints the 3 most recent matching emails that have attachments. Avoids opening the Gmail web UI for a quick attachment lookup.

---

## Requirements

**Must do:**
- Accept a query string as a CLI argument (e.g., `python search.py "from:boss report"`).
- Authenticate via OAuth 2.0 with read-only scope; persist the token for subsequent runs.
- Return the 3 most recent matching emails with attachments, newest-first.
- Per result: date (YYYY-MM-DD), sender, subject, attachment filenames.
- Print a clear message when fewer than 3 results (including zero) are found.

**Must not do:**
- Download or read attachment content.
- Mutate any email data (send, delete, modify).
- Expose credentials or tokens in output.
- Request broader OAuth scopes than needed.

---

## Solution

### Dependencies
- `google-api-python-client`, `google-auth-oauthlib`, `google-auth-httplib2`; stdlib only beyond these.

### Authentication

Gmail API with OAuth 2.0 installed-app flow. User places `credentials.json` (from Google Cloud Console) next to the script; `token.json` is written on first run and reused thereafter. Scope: `gmail.readonly` — narrowest that allows search, so consent shows read-only access only.

Missing `credentials.json` → exit with setup instructions. Expired token → auto-refreshed; if refresh fails, re-prompt consent.

**Assumption:** User can set up a GCP project, enable the Gmail API, and obtain `credentials.json` (one-time).

### Search

Endpoint: `users.messages.list` with effective query `<user_query> has:attachment` (printed on run; duplicate `has:attachment` is harmless). `maxResults=10`; Gmail returns newest-first by `internalDate`, so the first 3 are the target. Details fetched via `messages.get(format=metadata, metadataHeaders=[From,Subject,Date])` — headers + part structure only, no body.

Gmail returns messages, not threads; multiple replies in a thread may each appear. Acceptable for a simple script.

API errors (4xx/5xx) print a human-readable message and exit non-zero.

**Assumption:** `has:attachment` matches inline images too; named-file-only filtering would need `Content-Disposition` inspection (see Uncertainty).

### Output

```
Query: "from:boss report has:attachment"

[1] 2024-03-15  From: boss@example.com
    Subject: Q1 Report
    Attachments: report.pdf, summary.xlsx
...
```

Fewer than 3: `Found 1 matching email (fewer than 3 available).`  
Zero: `No emails found matching: "..."`

---

## Alternatives considered

**IMAP:** No extra packages, but requires an App Password (deprecated) and different search syntax. Rejected.  
**Third-party wrappers (`simplegmail`, etc.):** Extra dependency, no benefit over the official client. Rejected.

---

## Out of scope

Downloading attachments · pagination past page 1 · multiple accounts · send/compose · non-Gmail providers · GUI · installable packaging · retry logic.

---

## Uncertainty

- **"Returns":** Assumed stdout print. Library-function return would need a different output layer.
- **"Simple":** OAuth setup (credentials.json, browser consent) may feel non-trivial; unavoidable with the Gmail API.
- **`has:attachment` precision:** Includes inline images; named-file-only would require `Content-Disposition: attachment` filtering.
- **Error depth:** Basic messages sufficient; retries and detailed diagnostics are out of scope.
