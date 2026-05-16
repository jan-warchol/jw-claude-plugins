# Gmail Attachment Search Script — Implementation Plan

## Overview

A command-line Python script that accepts a search query from the user, searches Gmail for matching emails, and returns the 3 most recent results that contain attachments.

---

## Goals

- Accept a search query string as input (CLI argument or interactive prompt).
- Use the Gmail API to search for matching threads/messages.
- Filter results to only those that include at least one attachment.
- Return the 3 most recent qualifying emails, printing key metadata (sender, date, subject, attachment names).

---

## Non-Goals

- Downloading or saving attachment files to disk.
- Sending or modifying emails.
- Supporting multiple Gmail accounts.

---

## Architecture

```
gmail_search.py
│
├── CLI entry point          — parse args, call search
├── GmailClient              — wraps authentication + API calls
│   ├── authenticate()       — OAuth2 flow, token caching
│   ├── search_messages()    — run query via messages.list
│   ├── get_message()        — fetch full message by ID
│   └── has_attachment()     — inspect MIME parts for attachments
└── format_result()          — pretty-print email metadata
```

Single file, no unnecessary abstractions. No classes needed if the script stays small — plain functions are fine.

---

## Dependencies

| Package | Purpose |
|---|---|
| `google-auth` | OAuth2 credential handling |
| `google-auth-oauthlib` | OAuth2 browser-based login flow |
| `google-auth-httplib2` | HTTP transport for the API client |
| `google-api-python-client` | Gmail REST API wrapper |

Install:
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

---

## Authentication

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Gmail API**.
3. Create **OAuth 2.0 credentials** (Desktop app type), download `credentials.json`.
4. On first run, the script opens a browser for the user to grant read-only Gmail access.
5. The resulting token is cached in `token.json` for subsequent runs.

Required OAuth scope:
```
https://www.googleapis.com/auth/gmail.readonly
```

---

## Implementation Steps

### Step 1 — Project setup

```
gmail-attachments/
├── credentials.json    # from Google Cloud Console (gitignored)
├── token.json          # auto-generated on first run (gitignored)
├── gmail_search.py
└── requirements.txt
```

### Step 2 — Authentication function

```python
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_PATH = "token.json"
CREDS_PATH = "credentials.json"

def authenticate():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)
```

### Step 3 — Search messages

Use `messages.list` with the user's query. Gmail's search syntax is the same as the web UI (`has:attachment`, `from:`, `subject:`, etc.). To find emails with attachments, append `has:attachment` to the user's query automatically.

```python
def search_messages(service, query, max_results=20):
    full_query = f"{query} has:attachment"
    response = service.users().messages().list(
        userId="me",
        q=full_query,
        maxResults=max_results,
    ).execute()
    return response.get("messages", [])
```

The API returns results newest-first by default, so the first 3 results are already the most recent matching messages.

### Step 4 — Fetch message details

```python
def get_message(service, msg_id):
    return service.users().messages().get(
        userId="me",
        id=msg_id,
        format="full",
    ).execute()
```

### Step 5 — Extract attachment names

Walk the MIME payload parts recursively. A part is an attachment when it has a `filename` and a non-empty `body.attachmentId`.

```python
def get_attachment_names(payload):
    names = []
    parts = payload.get("parts", [])
    for part in parts:
        filename = part.get("filename")
        body = part.get("body", {})
        if filename and body.get("attachmentId"):
            names.append(filename)
        names.extend(get_attachment_names(part))  # recurse into nested parts
    return names
```

### Step 6 — Extract headers

```python
def get_header(message, name):
    headers = message["payload"].get("headers", [])
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""
```

### Step 7 — Main flow

```python
def main():
    query = sys.argv[1] if len(sys.argv) > 1 else input("Search query: ")
    service = authenticate()
    messages = search_messages(service, query)

    count = 0
    for msg_stub in messages:
        if count >= 3:
            break
        message = get_message(service, msg_stub["id"])
        attachments = get_attachment_names(message["payload"])
        if not attachments:
            continue  # guard: has:attachment is usually reliable but double-check
        print_result(message, attachments)
        count += 1

    if count == 0:
        print("No emails with attachments found for that query.")
```

### Step 8 — Output formatting

```
─────────────────────────────────────────────
From   : Alice <alice@example.com>
Date   : Fri, 15 May 2026 14:32:10 +0200
Subject: Q2 report
Attachments:
  • q2_report.pdf
  • data.xlsx
─────────────────────────────────────────────
```

---

## Edge Cases

| Case | Handling |
|---|---|
| Query returns fewer than 3 results | Print however many are found; note if zero |
| `has:attachment` returns false positives (inline images) | `get_attachment_names` filters by `attachmentId` presence |
| `credentials.json` missing | Print a clear error with setup instructions |
| Network / API error | Let the exception surface with its message; no silent swallowing |
| Token expired | `creds.refresh()` handles it transparently |

---

## Security Notes

- `credentials.json` and `token.json` must be added to `.gitignore`.
- The script requests only `gmail.readonly` — no write access.
- No attachment content is downloaded; only filenames are read from metadata.

---

## File: `requirements.txt`

```
google-auth>=2.0
google-auth-oauthlib>=1.0
google-auth-httplib2>=0.2
google-api-python-client>=2.0
```

---

## Usage

```bash
# First run — opens browser for OAuth consent
python gmail_search.py "invoice from:supplier@example.com"

# Subsequent runs — uses cached token
python gmail_search.py "project proposal"
```

---

## Estimated Complexity

- ~100–130 lines of Python.
- No external database, no framework, no background service.
- One-time OAuth setup; then fully automated on subsequent runs.
