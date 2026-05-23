# Gmail Attachment Search Script

## Overview

A command-line Python script that searches Gmail for emails matching a user-provided query and returns the last 3 matching emails that contain attachments.

## Functional Requirements

### Input
- The user provides a search query string as a command-line argument.
- The query follows Gmail search syntax (e.g., `from:boss@example.com`, `subject:invoice`, `after:2024/01/01`).

### Processing
- Authenticate with the Gmail API using OAuth 2.0.
- Search Gmail for messages matching the provided query.
- Filter results to only include messages that have at least one attachment.
- Return the 3 most recent such messages.

### Output
- For each of the (up to) 3 matching emails, print:
  - Date sent
  - Sender (`From` header)
  - Subject
  - List of attachment filenames and their sizes

## Non-Functional Requirements

- **Authentication**: Uses Gmail API with OAuth 2.0. Credentials are stored locally so the user only authenticates once.
- **Scope**: Requires read-only Gmail access (`gmail.readonly`).
- **Dependencies**: `google-auth`, `google-auth-oauthlib`, `google-api-python-client`.

## Out of Scope

- Downloading or saving attachments to disk.
- Modifying, deleting, or sending emails.
- Pagination beyond the first page of search results.
- Support for inline images (only named file attachments are counted).

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
