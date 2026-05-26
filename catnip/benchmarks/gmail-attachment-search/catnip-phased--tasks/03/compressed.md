# Gmail Attachment Search Script — Spec

## Overview

CLI Python script that authenticates with Gmail via OAuth2, searches emails by a user-supplied query, and prints metadata for the 3 most recent results that have attachments.

## Usage

**Input**: positional query string, passed directly to the Gmail API (full Gmail search syntax supported: `from:boss@example.com`, `subject:invoice`, etc.).

```
python gmail_search.py "from:invoices@acme.com"
```

**Output**: up to 3 results printed to stdout, separated by blank lines:

```
Subject: Q2 Invoice
From: billing@acme.com
Date: 2026-03-14 09:22
Attachments: invoice_q2.pdf, terms.docx
```

Prints fewer if fewer exist; prints a message if none match.

## Setup

**Dependencies**: `google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client`

```
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

**Authentication**: OAuth 2.0, scope `https://www.googleapis.com/auth/gmail.readonly`. Place `credentials.json` (from Google Cloud Console) in the working directory. First run opens a browser for consent; token is cached in `token.json` and auto-refreshed.

**Assumption**: user has a Google Cloud project with Gmail API enabled. If the consent screen is unpublished, only added test users can authenticate.

## Behaviour

1. Load/refresh OAuth token.
2. Call `users.messages.list` with the query, appending `has:attachment` if absent (reduces payload fetches). Returns IDs newest-first, up to 500/page.
3. For each ID, fetch full payload (`format=full`); treat MIME parts with a non-empty `filename` as attachments.
4. Stop after collecting 3; print results.

Only the first page (≤500 messages) is searched; if it yields fewer than 3 with attachments, print however many were found.

## Error Handling

- Missing `credentials.json`: actionable error with instructions to obtain it.
- No messages match: "No emails found matching query."
- No attachments among matches: "No matching emails with attachments found."
- API/network errors: print error, exit code 1.

## Design Choices

**Gmail API over IMAP**: Gmail's query engine supports labels, operators, and full-text; IMAP `SEARCH` does not.

**Append `has:attachment` + verify payload**: reduces unnecessary fetches while guarding against the API matching inline images that have no true attachment part.

**Inline images heuristic**: any MIME part with a non-empty `filename` is counted as an attachment regardless of `Content-Disposition` — a pragmatic heuristic that may occasionally include inline images.

**OAuth 2.0 over service account**: service accounts need domain-wide delegation (Workspace admin). OAuth 2.0 works for any Gmail account.

## Out of Scope

- Downloading attachment content; modifying or deleting emails.
- Pagination past the first page.
- Multiple accounts; interactive query input.
- Configurable result limit (`--limit N` deferred; hardcoded to 3).
