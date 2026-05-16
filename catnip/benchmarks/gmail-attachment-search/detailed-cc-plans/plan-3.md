# Plan: Gmail Attachment Search Script

## Goal

A command-line Python script that accepts a search query from the user, searches their Gmail inbox, and returns the 3 most recent matching emails that contain attachments.

---

## Approach

Use the Gmail MCP tools already available in this session to search threads and retrieve message details. The script will call those tools via the Claude API (using Claude as the backend), or — for a standalone deployable artifact — use the Gmail REST API directly via the `google-api-python-client` library with OAuth 2.0.

The plan below covers the **standalone script** path (no MCP dependency), which is more portable.

---

## Components

### 1. Authentication (`auth.py` or inline)

- Use `google-auth-oauthlib` to implement the OAuth 2.0 installed-app flow.
- Required Gmail scope: `https://www.googleapis.com/auth/gmail.readonly`
- Store the resulting token in `token.json` so the user only authenticates once.
- Refresh the token automatically when it expires.

**Steps:**
1. Load `credentials.json` (downloaded from Google Cloud Console).
2. If `token.json` exists and is valid, load it; otherwise run the browser-based OAuth flow.
3. Return an authenticated `googleapiclient.discovery.Resource` (the Gmail service object).

---

### 2. Search (`search_threads`)

- Call `users.messages.list` with:
  - `userId = "me"`
  - `q = <user_query>` — passed directly to Gmail's search syntax (supports `has:attachment`, `from:`, `subject:`, date ranges, etc.)
- The query does **not** need to include `has:attachment`; we filter for attachments ourselves so the user's query stays flexible.
- Request enough results to find 3 with attachments (start with `maxResults=20`, page if needed).

---

### 3. Attachment Detection (`has_attachment`)

Gmail's `messages.list` returns only message IDs. For each candidate:

1. Fetch the message with `format="metadata"` and `metadataHeaders=["Subject", "From", "Date"]`.
2. Inspect `payload.parts` recursively: a message has an attachment if any part has a non-empty `filename` field **or** a `mimeType` that is not `text/plain` / `text/html` and has a non-zero `body.size`.
3. Stop once 3 qualifying messages are found (lazy evaluation — avoid fetching more than necessary).

---

### 4. Result Formatting (`format_result`)

For each of the (up to) 3 matching messages, return a dictionary:

```python
{
    "id": str,           # Gmail message ID
    "subject": str,
    "from": str,
    "date": str,         # RFC 2822 date string from headers
    "snippet": str,      # Gmail-provided plain-text preview
    "attachments": [     # list of attachment names/sizes
        {"filename": str, "mimeType": str, "size_bytes": int}
    ]
}
```

Print each result as a readable block to stdout. Optionally support `--json` flag to emit raw JSON.

---

### 5. CLI Entry Point (`main.py`)

```
usage: main.py [-h] [--json] query

positional arguments:
  query       Gmail search query (e.g. "from:boss subject:report")

optional arguments:
  -h, --help  show this help message and exit
  --json      Output results as JSON instead of human-readable text
```

Use Python's `argparse` module.

---

## File Layout

```
gmail-attachments/
├── credentials.json      # downloaded from Google Cloud Console (not committed)
├── token.json            # written at runtime after first auth (not committed)
├── main.py               # CLI entry point + result formatter
├── auth.py               # OAuth flow + service construction
├── search.py             # search + attachment-detection logic
├── requirements.txt
└── .gitignore
```

---

## Dependencies (`requirements.txt`)

```
google-api-python-client>=2.0
google-auth-httplib2>=0.1
google-auth-oauthlib>=1.0
```

---

## Data Flow

```
User runs: python main.py "from:alice invoice"
         │
         ▼
auth.py  ──► load/refresh token ──► Gmail service object
         │
         ▼
search.py ──► messages.list(q="from:alice invoice", maxResults=20)
           ──► for each message ID:
                   messages.get(format="metadata")
                   has_attachment? ──► yes → collect → stop when 3 found
         │
         ▼
main.py  ──► format & print results
```

---

## Error Handling

| Scenario | Handling |
|---|---|
| `credentials.json` missing | Print instructions to download from Google Cloud Console and exit with code 1 |
| OAuth flow cancelled by user | Catch `KeyboardInterrupt`, exit gracefully |
| No messages match the query | Print "No results found." and exit 0 |
| Fewer than 3 results with attachments | Return however many were found, note the count |
| HTTP 429 / quota exceeded | Retry with exponential backoff (max 3 retries) |
| HTTP 401 / token invalid | Delete `token.json`, re-run auth flow automatically |

---

## Implementation Order

1. `auth.py` — OAuth flow (testable in isolation: `python auth.py` should print "Authenticated successfully").
2. `search.py` — `search_messages(service, query, max_results)` returning raw message metadata.
3. `search.py` — `has_attachment(payload)` recursive helper.
4. `search.py` — `collect_with_attachments(service, query, limit=3)` combining the above.
5. `main.py` — `format_result(msg)` + `argparse` wiring + `main()`.
6. End-to-end test with a real query.

---

## Google Cloud Console Setup (prerequisite)

1. Create a project at [console.cloud.google.com](https://console.cloud.google.com).
2. Enable the **Gmail API**.
3. Create OAuth 2.0 credentials → **Desktop app** → download `credentials.json`.
4. Add the test user's email (`lemniskata.bernoullego@gmail.com`) to the OAuth consent screen's **Test users** list (required while the app is in "Testing" status).

---

## Out of Scope

- Downloading/saving attachment files (detection only).
- Sending or modifying emails.
- Pagination beyond the first page needed to find 3 results.
- A GUI or web interface.
