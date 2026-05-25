# Gmail Attachment Search Script

## Overview

A CLI Python script that searches Gmail for emails matching a user query and returns the 3 most recent results containing attachments.

## Functional Requirements

**Input**: A Gmail search query string as a command-line argument (standard Gmail syntax, e.g. `from:boss@example.com subject:invoice`).

**Processing**:
- Authenticate with Gmail API via OAuth 2.0.
- Append `has:attachment` to the query to filter server-side; return the 3 most recent results by `internalDate` (fewer if unavailable).
- Enumerate attachment filenames and sizes via client-side MIME inspection.

**Output**: For each matching email, print date (YYYY-MM-DD), sender, subject, and attachment filenames with sizes (KB, rounded). If no matches: print `No matching emails with attachments found.` and exit 0.

**Error handling**:
- Missing `credentials.json`: print instructions for obtaining it, exit non-zero.
- API/network errors: print error, exit non-zero.
- Expired token: auto-refresh; re-prompt OAuth only if refresh token is also invalid.

## Non-Functional Requirements

- `credentials.json` (OAuth client secret from Google Cloud Console) required on first run; token cached as `token.json` for subsequent runs.
- Scope: `gmail.readonly`.
- Dependencies: `google-auth`, `google-auth-oauthlib`, `google-api-python-client`.

## Out of Scope

Downloading attachments, modifying/sending emails, pagination, inline images, configurable result count.

## Usage Example

```
python search_attachments.py "from:boss@example.com invoice"
```

```
1. 2024-03-15  From: boss@example.com  Subject: Q1 Invoice
   Attachments: invoice_q1.pdf (245 KB)

2. 2024-02-14  From: boss@example.com  Subject: February Invoice
   Attachments: invoice_feb.pdf (198 KB), expenses.xlsx (34 KB)
```
