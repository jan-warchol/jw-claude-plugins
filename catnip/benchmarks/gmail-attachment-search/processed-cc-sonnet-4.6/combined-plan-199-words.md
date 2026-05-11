# Gmail Attachment Search Script

**Goal:** Python CLI that accepts a search query, searches Gmail for matching emails with attachments, and returns the 3 most recent results.

## Prerequisites

- Python 3.8+; dependencies: `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib` (via `requirements.txt`)
- Google Cloud project with Gmail API enabled; OAuth 2.0 Desktop App credentials downloaded as `credentials.json`

## File Structure

```
gmail_search/
├── search_gmail.py
├── credentials.json    # user-provided; add to .gitignore
├── token.json          # auto-generated; add to .gitignore
└── requirements.txt
```

## Implementation

**Auth:** Load `credentials.json`; check for cached `token.json` — if missing or expired, launch OAuth browser flow and save token. Scope: `gmail.readonly` (least privilege). On silent refresh failure, delete `token.json` and prompt re-auth.

**Search:** Build query as `({user_query}) has:attachment` — server-side filtering. Call `messages().list(userId="me", q=full_query, maxResults=3)`, then `messages().get(format="full")` per ID to retrieve `From`, `Subject`, `Date` headers and walk `payload.parts` for non-empty `filename` fields.

**CLI:** Accept query via `argparse`; fall back to interactive prompt if no argument given.

```bash
python search_gmail.py "invoice from:boss@example.com"
```

**Output per result:**
```
--- Email 1 ---
Date:        Thu, 20 Apr 2026 14:32:00 +0000
From:        sender@example.com
Subject:     Q1 Invoice
Attachments: invoice.pdf, receipt.png
```

## Error Handling

| Scenario | Response |
|---|---|
| `credentials.json` missing | Print setup instructions and exit |
| No results | Print friendly message and exit |
| API / network error | Catch `HttpError`, print message, exit |
| Token expired, silent refresh fails | Delete `token.json`, prompt re-auth |
| Missing email headers | Fall back to `"(unknown)"` |
