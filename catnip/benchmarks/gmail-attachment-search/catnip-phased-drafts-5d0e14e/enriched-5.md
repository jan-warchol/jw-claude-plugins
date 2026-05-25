# Gmail Attachment Search Script

## Overview

A command-line Python script that searches Gmail for emails matching a user-provided query and returns the last 3 matching emails that contain attachments.

## Functional Requirements

### Input
- The user provides a search query string as a command-line argument.
- The query follows Gmail search syntax (e.g., `from:boss@example.com`, `subject:invoice`, `after:2024/01/01`).

### Processing
- Authenticate with the Gmail API using OAuth 2.0.
- Search Gmail by appending `has:attachment` to the user's query, filtering attachment-free messages server-side.
- Return the 3 most recent results, ranked by Gmail's internal timestamp (`internalDate`). If fewer than 3 exist, return all available.

### Output
- For each of the (up to) 3 matching emails, print:
  - Date sent (YYYY-MM-DD)
  - Sender (`From` header)
  - Subject
  - List of attachment filenames and sizes (in KB, rounded to nearest integer)
- If no matching emails are found, print `No matching emails with attachments found.` and exit with status 0.

### Error Handling
- Missing `credentials.json`: print an actionable message explaining how to obtain it, then exit non-zero.
- API or network errors: print the error and exit non-zero.
- Expired token: refresh automatically; re-prompt OAuth only if the refresh token is also invalid.

## Non-Functional Requirements

- **Authentication**: Users must supply `credentials.json` (OAuth client secret downloaded from Google Cloud Console) on first run. After authenticating, the token is saved as `token.json` in the working directory so subsequent runs skip the browser prompt.
- **Scope**: Requires read-only Gmail access (`gmail.readonly`).
- **Dependencies**: `google-auth`, `google-auth-oauthlib`, `google-api-python-client`.

## Design Notes

Appending `has:attachment` to the query filters attachment-free messages at the search level, avoiding unnecessary detail fetches. Client-side MIME inspection is still required to enumerate filenames and sizes, since the Gmail search API does not return attachment metadata directly.

## Out of Scope

- Downloading or saving attachments to disk.
- Modifying, deleting, or sending emails.
- Pagination beyond the first page of search results.
- Support for inline images (only named file attachments are counted).
- Configurable result count (fixed at 3).

## Assumptions

- The user has a Google account and can create OAuth 2.0 credentials in Google Cloud Console.
- Typical usage stays within Gmail API free-tier quota limits.

## Usage Example

```
python search_attachments.py "from:boss@example.com invoice"
```

Expected output:
```
1. 2024-03-15  From: boss@example.com  Subject: Q1 Invoice
   Attachments: invoice_q1.pdf (245 KB)

2. 2024-02-14  From: boss@example.com  Subject: February Invoice
   Attachments: invoice_feb.pdf (198 KB), expenses.xlsx (34 KB)

3. 2024-01-10  From: boss@example.com  Subject: January Invoice
   Attachments: invoice_jan.pdf (210 KB)
```
