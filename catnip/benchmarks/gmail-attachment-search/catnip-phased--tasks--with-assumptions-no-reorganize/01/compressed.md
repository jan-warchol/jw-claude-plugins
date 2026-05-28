# Spec: Gmail Attachment Search Script

## Objective

A Python CLI script that authenticates with Gmail, searches by a user-provided query, and prints the 3 most recent matching emails that have attachments.

## Requirements

**Must do:**
- Accept a search query via CLI argument or interactive prompt
- Authenticate with Gmail via OAuth2; cache the token for subsequent runs
- Return up to 3 most-recent matching emails (print a note if fewer than 3 exist)
- Display per result: subject, sender, date, attachment filenames and sizes
- Print setup instructions if `credentials.json` is missing

**Must not:**
- Download attachment content (metadata only)
- Modify, move, or delete emails
- Store credentials beyond what Google's OAuth2 flow requires

## Solution

**Authentication:** `google-auth-oauthlib` + `google-api-python-client` with `credentials.json` from Google Cloud Console. OAuth2 consent flow on first run; token persisted to `token.json` in the working directory. Scope: `gmail.readonly`.

**Search:** `gmail.users().messages().list(q="<user_query> has:attachment", maxResults=3)`. Results are newest-first by default. Duplicate `has:attachment` in the query is harmless — Gmail deduplicates silently.

**Detail fetch:** `gmail.users().messages().get(format="metadata", metadataHeaders=["Subject","From","Date"])`. Walk `payload.parts` recursively; include parts where `filename` is non-empty and `body.size > 0`, skipping `Content-Disposition: inline` to exclude embedded signature images.

**Output:** Plain-text blocks to stdout, separated by a divider:
```
From:    Alice <alice@example.com>
Date:    Wed, 28 May 2026 10:15:00 +0000
Subject: Q2 Report
Attachments:
  - report.pdf (142 KB)
  - data.xlsx (38 KB)
```

**Error handling:**
- Missing `credentials.json`: print setup instructions, exit non-zero
- `RefreshError`: delete `token.json`, re-run OAuth flow
- API/network errors: print human-readable message, exit; no silent swallowing

**Dependencies:** `google-api-python-client`, `google-auth-oauthlib`, `google-auth-httplib2`

**Entry point:** `python gmail_search.py "<query>"`

## Alternative solutions considered

- **`imaplib`:** No Cloud Console setup, but app passwords are being phased out. Gmail API is the correct modern approach.
- **Third-party wrappers (`simplegmail` etc.):** Less boilerplate but opaque dependency; official client is thin enough to use directly.

## Out of scope

Downloading attachments, pagination beyond 3 results, multiple accounts, write operations, installable packaging.

## Uncertainty

- **OAuth setup:** User must create a GCP project, enable Gmail API, and obtain `credentials.json`. Script prints instructions if it's missing; the setup itself is out of scope.
- **Output format:** "Returns" is assumed to mean stdout. No JSON/CSV unless requested.
- **"Last 3":** Newest by API default sort (received date); no secondary sort.
- **Inline filtering:** Non-empty `filename` + skip `Content-Disposition: inline` should correctly exclude signature images, but malformed MIME may cause edge-case false positives.
- **Quota:** A single run costs ~20 quota units (well within the free 1B/day limit).
