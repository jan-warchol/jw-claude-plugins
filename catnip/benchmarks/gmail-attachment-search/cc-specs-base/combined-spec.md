# Spec: Gmail Attachment Search Script

## Overview

A Python command-line script that accepts a search query, searches the user's Gmail inbox, and
returns the 3 most recent matching emails that contain attachments.

## Inputs

- `query` (required, positional CLI argument): A Gmail search query string (e.g.
  `"from:boss@example.com"`, `"subject:invoice"`).

## Output

For each of the up to 3 matching emails (most recent first), print to stdout:

- Date received
- Sender (`From` header)
- Subject
- List of attachment filenames

If fewer than 3 matching emails with attachments exist, print however many are found. If none are
found, print a clear "no results" message and exit with code 0.

## Behavior

1. Authenticate with Gmail using OAuth 2.0 (prompt the user to authorize on first run).
2. Append `has:attachment` to the user's query before searching so only emails with attachments are
   returned.
3. Retrieve results sorted by date descending; take the first 3.
4. For each result, fetch the message detail to extract headers and attachment filenames.
5. Print results in a human-readable format.

## Authentication

- Use OAuth 2.0 via the Gmail API (`google-auth`, `google-auth-oauthlib`,
  `google-api-python-client`).
- Credentials file: `credentials.json` in the working directory (OAuth 2.0 client secret, downloaded
  from Google Cloud Console).
- Token cache: `token.json` (auto-created on first run, reused on subsequent runs).
- Required OAuth scope: `https://www.googleapis.com/auth/gmail.readonly`.
- On first run, the script opens a browser for the user to authorize access.

## Dependencies

```
google-auth
google-auth-oauthlib
google-auth-httplib2
google-api-python-client
```

## Error Handling

- Missing `credentials.json`: print a clear error message explaining how to obtain it and exit with
  code 1.
- Gmail API errors (rate limit, network failure): print the error message and exit with code 1.
- No results: print `"No emails with attachments found matching query: <query>"` and exit with
  code 0.

## Example Usage

```bash
python gmail_attachment_search.py "from:boss@example.com invoice"
```

```
1. 2026-04-28  From: boss@example.com  Subject: Q1 Invoice
   Attachments: invoice_q1.pdf

2. 2026-03-15  From: boss@example.com  Subject: Q4 Invoice
   Attachments: invoice_q4.pdf, summary.xlsx

3. 2026-02-01  From: boss@example.com  Subject: Annual Report
   Attachments: annual_report.pdf
```

## Out of Scope

- Downloading attachment contents.
- Sending, modifying, labeling, or deleting emails.
- Pagination beyond the first API response page (the Gmail API returns up to 100 results per page;
  retrieving the top 3 always fits in a single page).
- Support for multiple Gmail accounts.
