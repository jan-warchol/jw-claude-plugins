# Spec: Gmail Search with Attachment Filter

## Objective

Build a simple Python CLI script that authenticates with Gmail, runs a user-provided search query, and returns the 3 most recent matching emails that have at least one attachment. The primary use case is quick ad-hoc retrieval of attachment-bearing emails without navigating the Gmail web UI.

---

## Requirements

**Must do:**
- Accept a search query string from the user (CLI argument or stdin prompt)
- Authenticate with Gmail using OAuth 2.0
- Search Gmail using the provided query, additionally filtered to messages with attachments
- Return the 3 most recent matching emails that contain at least one attachment
- For each returned email, display: subject, sender, date, and attachment filename(s)

**Must not:**
- Download or save attachment content to disk (out of scope for this script)
- Modify, delete, or send any emails
- Require a persistent server or daemon process

---

## Solution

**Authentication:** Use the Gmail API via `google-api-python-client` + `google-auth-oauthlib`. On first run, the OAuth flow opens a browser for the user to authorize the app; credentials are cached in a local `token.json` file for subsequent runs.

**Search:** Call `users.messages.list` with the user-supplied query string, appending `has:attachment` to ensure only emails with attachments are matched. Request up to the first page of results (default 100), sorted by recency (Gmail's default ordering).

**Filtering to 3:** Take the first 3 message IDs returned by the list call (Gmail returns newest first). For each, call `users.messages.get` with `format=metadata` and headers `[Subject, From, Date]`, plus inspect `payload.parts` to collect attachment filenames.

**Output:** Print a human-readable summary for each of the 3 emails to stdout.

**Dependencies:**
- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

**Credentials setup:** The user must create a Google Cloud project, enable the Gmail API, and download `credentials.json` (OAuth 2.0 desktop client). The script reads this file from the working directory.

---

## Alternative solutions considered

- **`imaplib` / `IMAPClient`:** Standard IMAP access would avoid the Google API SDK but requires enabling "Less secure app access" (deprecated) or App Passwords, and IMAP search syntax differs from Gmail's. Gmail API is the recommended modern approach.
- **`simplegmail` / third-party wrappers:** Simpler API surface but adds an opaque dependency; the official SDK is straightforward enough for this scope.

---

## Out of scope

- Downloading or saving attachment files
- Pagination beyond the first result page
- Support for non-Gmail accounts or generic IMAP
- A GUI or web interface
- Batch/scheduled execution

---

## Uncertainty

- **`has:attachment` query suffix:** Appending it to the user query with a space should work in all cases, but if the user already includes `has:attachment` in their query, it would be duplicated (harmless, but worth noting).
- **Attachment detection in nested MIME parts:** Some emails have deeply nested `multipart` structures. Inspecting only the top-level `payload.parts` may miss attachments in nested parts; a recursive walk may be needed.
- **Token refresh / expiry:** The cached `token.json` approach handles refresh automatically via the library, but first-run UX (browser pop-up) may be surprising in headless environments.
- **Result count < 3:** If fewer than 3 matching emails exist, the script should degrade gracefully rather than error.
