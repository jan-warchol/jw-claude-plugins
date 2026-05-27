# Gmail Attachment Search Script

## Overview

CLI Python script that queries Gmail via OAuth 2.0 and prints the three most recent matching emails with attachments. An attachment is any MIME part with a non-empty `filename` (includes named inline images; unnamed inline content is excluded).

## Authentication

- Gmail API via `google-auth` and `google-api-python-client`.
- Reads `credentials.json` (Google Cloud Console download); must be an **installed-application** client, not a service account.
- First run opens a browser for consent; token cached in `token.json` and auto-refreshed.
- Scope: `https://www.googleapis.com/auth/gmail.readonly`.
- Browser required — headless/server environments are not supported.

## Interface

### Input

`--query` / `-q` — search string passed directly to the Gmail API `q` parameter.

```
python gmail_search.py --query "invoice from:billing@example.com"
```

### Output

```
--- Email 1 ---
Date:    <date>
From:    <sender>
Subject: <subject>
Attachments:
  - filename.pdf (application/pdf, 45 KB)
  - photo.jpg (image/jpeg, 200 KB)
```

File size from the part's `size` field, displayed in KB (rounded).

## Core Logic

1. Authenticate and build the Gmail API service.
2. `users.messages.list` with the query; fetch up to 100 results (newest first).
3. For each result, retrieve via `users.messages.get` with `format=full`.
4. Recursively walk the MIME tree; collect parts with a non-empty `filename`.
5. Email qualifies if at least one such part exists.
6. Stop at 3 qualifying emails or when results are exhausted.

## Error Handling

| Condition | Behavior |
|---|---|
| Missing `credentials.json` | Print setup instructions, exit |
| No results match query | `"No emails found matching query: <query>"` |
| Fewer than 3 with attachments | Print however many were found |
| API error | Print error message, exit non-zero |

## Design Decisions

**Gmail API over IMAP.** The API returns structured MIME metadata without downloading bodies and accepts Gmail's native query syntax. IMAP would require raw MIME parsing and re-implementing Gmail's query semantics.

**`format=full`, no attachment download.** Returns the full MIME tree with part metadata (filename, type, size) but not attachment bytes — sufficient for detection and display without fetching content.

**100-result cap, no pagination.** This is a quick lookup tool, not a bulk processor; paginating for edge cases adds complexity without meaningful benefit.

**Single account only.** Matches the scope of a personal utility script.

## Risks

- Gmail API quota (~5 units per `messages.get`, 1B units/day default) is not a concern for this use case.

## Setup

`requirements.txt`:
```
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

Files:
```
gmail_search.py       # main script
credentials.json      # OAuth client secret (user-provided, not committed)
token.json            # stored token (auto-generated, not committed)
requirements.txt
```
