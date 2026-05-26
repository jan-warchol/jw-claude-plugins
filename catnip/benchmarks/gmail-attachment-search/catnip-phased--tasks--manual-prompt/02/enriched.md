# Gmail Attachment Search Script — Spec

## Overview

A command-line Python script that authenticates with Gmail via OAuth2, accepts a search query from the user, and returns the three most recent emails matching that query which contain at least one attachment. Each result includes the sender, subject, date, and a list of attachment filenames.

## Functional Requirements

### Input
- A single positional CLI argument: the Gmail search query string (e.g., `"from:boss invoice"`).
- The query follows Gmail's standard search syntax, passed through unchanged to the API.
- The script automatically appends `has:attachment` to the user query before sending it to the API, so the user does not need to include it themselves. This is done silently; the modified query is not shown.

### Processing
1. Authenticate with the Gmail API using OAuth2 (credentials stored locally).
2. Call `users.messages.list` with the augmented query (`<user_query> has:attachment`), requesting up to 10 results per page.
3. Fetch full message details (`format=full`) for each result, newest first, until 3 messages with at least one non-inline attachment are collected or the result set is exhausted.
4. An attachment is any MIME part where `filename` is non-empty and `Content-Disposition` is `attachment` (not `inline`). Inline images embedded in HTML emails are excluded.
5. Stop after collecting 3 such messages; do not fetch further pages.

### Output
Print to stdout a structured summary for each of the up to 3 matched messages:

```
--- Email 1 ---
From:    alice@example.com
Subject: Q1 Invoice
Date:    Mon, 12 May 2025 09:14:03 +0000
Attachments:
  - invoice_q1.pdf (application/pdf)
  - terms.docx (application/vnd.openxmlformats...)
```

If fewer than 3 matching emails are found, print however many exist. If none are found, print: `No matching emails with attachments found.`

## Authentication

- Use `google-auth-oauthlib` and `google-api-python-client`.
- On first run, open a browser for OAuth2 consent and save the resulting token to `token.json` in the working directory.
- On subsequent runs, load `token.json` and refresh automatically if expired.
- Required OAuth2 scope: `https://www.googleapis.com/auth/gmail.readonly`.
- The script reads `credentials.json` (downloaded from Google Cloud Console) from the working directory. The credentials must be for a **Desktop app** OAuth2 client (not a web app or service account).

## Dependencies

```
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

## Usage

```
python gmail_search.py "<query>"
```

Example:

```
python gmail_search.py "from:finance"
```

## Error Handling

- Missing `credentials.json`: print an instructional error and exit with code 1.
- API errors (quota exceeded, network failure): print the error message and exit with code 1.
- Invalid or empty query string: print usage hint and exit with code 1.
- Expired token that cannot be refreshed (e.g., revoked): delete `token.json` and prompt the user to re-run for a fresh OAuth2 flow.

## Design Choices and Trade-offs

**Auto-appending `has:attachment`:** The script adds `has:attachment` to the query rather than filtering purely client-side. This offloads attachment filtering to Gmail's server, reducing the number of messages fetched and API calls made. The trade-off is that the query sent to Gmail differs from what the user typed; this is acceptable because the script's stated purpose is explicitly to find emails with attachments.

**`format=full` vs `format=metadata`:** Fetching `format=full` is required to inspect MIME parts and identify attachment filenames. `format=metadata` would be more efficient but cannot reliably detect or name attachments.

**No pagination beyond 3 results:** Because `has:attachment` is in the API query, the first page of results (10 messages) is very likely to satisfy the 3-result requirement. Deep pagination is excluded as a non-goal.

## Assumptions and Risks

- **Assumption:** The user has already created a Google Cloud project with the Gmail API enabled and downloaded `credentials.json` as a Desktop OAuth2 client.
- **Assumption:** The script is run in an environment with a browser available for the initial OAuth2 consent flow.
- **Risk:** `token.json` is stored in plaintext. Users should ensure the working directory is not publicly accessible.
- **Risk:** Gmail API has a daily quota (1 billion quota units/day; `messages.get` costs 5 units each). Fetching up to 10 full messages per run is well within normal limits.

## Non-Goals

- Downloading attachment content.
- Pagination beyond the first page of results.
- Support for multiple Gmail accounts.
- Any GUI or interactive mode.
- Handling inline images as attachments.
