# Gmail Attachment Search — Spec

## Overview

CLI Python script: authenticates with Gmail via OAuth2, searches emails by a user-supplied query, prints the 3 most-recent results that have at least one attachment.

## Setup

**Dependencies:**
```
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

**Authentication:** Requires `credentials.json` (from Google Cloud Console) in the working directory. First run opens a browser for OAuth2 consent and saves `token.json`; subsequent runs load and auto-refresh it. Scope: `gmail.readonly`.

## Interface

```bash
python gmail_search.py "<query>"
```

Required positional argument: any valid Gmail search query, passed to the API unmodified.

```bash
python gmail_search.py "from:alice subject:invoice"
python gmail_search.py "has:attachment newer_than:7d"
```

## Behavior

1. Authenticate with the Gmail API.
2. Search with the provided query; request up to 100 results, newest-first.
3. For each result, fetch the full payload (`format=full`) and inspect MIME parts.
4. A message qualifies if it has at least one part with `Content-Disposition: attachment`, or a non-empty `filename` not flagged `inline` (excludes embedded HTML images).
5. Collect the first 3 qualifying messages; stop early once found or after 100 results — no further pagination.
6. Print results.

### Output

```
Subject: <subject>
From:    <sender>
Date:    <date as provided by Gmail>
Attachments:
  - <filename> (<mime-type>, <size> bytes)
---
```

Nameless attachments display as `(unnamed)`. When no qualifying emails exist:

```
No emails with attachments found matching: <query>
```

### Error Handling

- Missing `credentials.json`: explain where to obtain it; exit 1.
- Expired/revoked `token.json`: prompt re-authentication; exit 1.
- API error (network, quota): print error; exit 1.
- Invalid/empty query: passed through; Gmail returns zero results.

## Design Notes

**Query passed as-is:** `has:attachment` is not appended automatically — keeps the query transparent and composable at the cost of slightly more API calls on non-matching results.

**100-result cap, no pagination:** Sufficient for a simple utility; users needing deeper results can tighten their query.

**`format=full`:** One call per message vs. a two-step metadata+body fetch; larger payloads are acceptable given at most 3 full messages are retrieved.

**Exclusions:** no attachment download (metadata only); single account only; result count fixed at 3; no JSON output mode.

**Assumptions/risks:** First-run OAuth needs a local browser. API quota is not a concern (100 list calls + 3 full fetches ≪ 250 units/s). `token.json` holds a long-lived refresh token — treat as a secret, exclude from version control.
