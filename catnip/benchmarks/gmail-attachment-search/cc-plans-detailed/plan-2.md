# Plan: Gmail Attachment Search Script

## Overview

A command-line Python script that accepts a search query from the user, searches their Gmail inbox
via the Gmail API, and prints details for the last 3 matching emails that contain at least one
attachment.

---

## 1. Prerequisites & Dependencies

| Dependency                 | Purpose                         |
| -------------------------- | ------------------------------- |
| `google-auth-oauthlib`     | OAuth 2.0 flow for user consent |
| `google-auth-httplib2`     | HTTP transport for Google auth  |
| `google-api-python-client` | Gmail REST API client           |

Install with:

```
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

---

## 2. Google Cloud Setup (one-time, manual)

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Gmail API** for the project.
3. Create **OAuth 2.0 credentials** (Desktop app type).
4. Download the credentials JSON and save it as `credentials.json` in the project directory.
5. Add the user's Gmail address as a test user (while the app is in "testing" mode).

The script will store a refresh token in `token.json` after the first successful login so subsequent
runs skip the browser flow.

---

## 3. Authentication Flow

```
credentials.json present?
        |
        v
token.json present and valid? ──yes──> use existing credentials
        |
        no
        v
Launch browser OAuth consent screen
        |
        v
User grants access → save token to token.json
        |
        v
Return authenticated gmail service object
```

- Scope required: `https://www.googleapis.com/auth/gmail.readonly`
- If `token.json` is expired, `google-auth-oauthlib` refreshes it automatically using the stored
  refresh token.

---

## 4. Script Structure

```
gmail_attachments/
├── credentials.json   # downloaded from Google Cloud (not committed to git)
├── token.json         # auto-generated on first run (not committed to git)
└── search_attachments.py
```

### `search_attachments.py` — top-level layout

```python
def authenticate() -> Resource
def search_messages(service, query: str, max_results: int = 100) -> list[dict]
def has_attachment(message: dict) -> bool
def format_message(service, message: dict) -> dict
def main()
```

---

## 5. Detailed Function Specs

### `authenticate() -> Resource`

- Loads `token.json` if it exists and is valid.
- Falls back to the OAuth browser flow using `credentials.json`.
- Saves updated credentials back to `token.json`.
- Returns an authenticated `googleapiclient.discovery.Resource` for the Gmail API (v1).

### `search_messages(service, query: str, max_results: int) -> list[dict]`

- Calls `service.users().messages().list()` with:
  - `userId="me"`
  - `q=query` — the user-provided search string, passed directly to Gmail's search engine (supports
    all Gmail search operators, e.g. `from:alice`, `subject:invoice`, `has:attachment`)
  - `maxResults=max_results`
- Handles pagination via `nextPageToken` if needed, but stops once `max_results` message stubs are
  collected.
- Returns a list of message stubs: `[{"id": "...", "threadId": "..."}, ...]`.

### `has_attachment(message: dict) -> bool`

- Inspects the `payload` of a fully-fetched message.
- Returns `True` if any part in `payload["parts"]` has `"filename"` set to a non-empty string and
  `mimeType != "text/plain"` and `mimeType != "text/html"`.
- Handles messages with no `"parts"` key (single-part messages) gracefully — returns `False`.

### `format_message(service, message: dict) -> dict`

- Fetches full message via
  `service.users().messages().get(userId="me", id=message["id"], format="full")`.
- Extracts from headers:
  - `Subject`
  - `From`
  - `Date`
- Collects attachment names: filenames from all parts where `filename` is non-empty.
- Returns:
  ```python
  {
      "id": str,
      "subject": str,
      "from": str,
      "date": str,
      "attachments": list[str],   # filenames
  }
  ```

### `main()`

1. Parse `query` from `sys.argv[1]` (or prompt the user interactively if no argument is given).
2. Call `authenticate()` to get the service object.
3. Call `search_messages(service, query)` to get up to 100 message stubs. Gmail returns results
   newest-first by default, so no explicit sort is needed.
4. Iterate through stubs, fetching each full message, and collect those where `has_attachment()` is
   `True`.
5. Stop after collecting 3 such messages.
6. Print a formatted summary for each of the 3 results.

---

## 6. Output Format

```
Found 3 emails matching "<query>" with attachments:

────────────────────────────────────────
#1
Subject : Q1 Invoice
From    : billing@example.com
Date    : Fri, 10 May 2026 14:23:01 +0000
Files   : invoice_q1.pdf, terms.docx
────────────────────────────────────────
#2
...
```

---

## 7. Error Handling

| Condition                            | Handling                                             |
| ------------------------------------ | ---------------------------------------------------- |
| `credentials.json` missing           | Print clear message and exit with code 1             |
| OAuth flow cancelled by user         | Catch `SystemExit`/`KeyboardInterrupt`, exit cleanly |
| API quota exceeded                   | Catch `HttpError 429`, print retry message           |
| No matching emails found             | Print "No emails found for query." and exit 0        |
| Fewer than 3 emails with attachments | Print however many were found (0–2) with a note      |

---

## 8. Security & Privacy Notes

- `credentials.json` and `token.json` must be added to `.gitignore`.
- The script requests read-only scope (`gmail.readonly`) — it cannot send, delete, or modify any
  email.
- No email body content or attachment bytes are downloaded; only metadata (headers + filenames) is
  read.

---

## 9. Implementation Steps (ordered)

1. Set up the Google Cloud project and download `credentials.json`.
2. Install dependencies (`pip install ...`).
3. Implement `authenticate()` and verify the OAuth flow works end-to-end.
4. Implement `search_messages()` and print raw stubs to verify the API call.
5. Implement `has_attachment()` with a few test message IDs.
6. Implement `format_message()` and verify header extraction.
7. Wire everything together in `main()` with the stop-at-3 logic.
8. Add error handling for all edge cases listed above.
9. Test with several queries: one with results, one with no results, one where fewer than 3 have
   attachments.

---

## 10. Future Enhancements (out of scope for v1)

- `--download` flag to save attachment files locally.
- Support for multiple Gmail accounts.
- Output as JSON (`--json` flag) for piping into other tools.
- Batch API calls to reduce per-message round-trips.
