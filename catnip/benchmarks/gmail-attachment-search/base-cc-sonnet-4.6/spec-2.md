# Spec: Gmail Attachment Search Script

## Overview

A command-line Python script that accepts a search query, searches the user's Gmail inbox, and returns the 3 most recent matching emails that contain attachments.

## Inputs

- `query` (required, positional CLI argument): A Gmail search query string (e.g. `"from:boss@example.com"`, `"subject:invoice"`).

## Outputs

Prints to stdout a list of up to 3 emails, each showing:
- Date sent
- Sender (`From`)
- Subject
- List of attachment filenames

If fewer than 3 matching emails with attachments exist, print however many are found. If none are found, print a message indicating no results.

## Behavior

1. Authenticate with Gmail using OAuth2 (Google API credentials).
2. Run a Gmail search combining the user-provided query with `has:attachment`.
3. Retrieve results sorted by date descending (most recent first).
4. Return the top 3 results.
5. For each result, fetch the message metadata and part list to extract sender, date, subject, and attachment filenames.

## Authentication

- Use the Gmail API via `google-auth` and `google-api-python-client`.
- Credentials file: `credentials.json` (OAuth2 client secret, downloaded from Google Cloud Console).
- Token cache: `token.json` (auto-created on first run, reused on subsequent runs).
- Required OAuth scope: `https://www.googleapis.com/auth/gmail.readonly`.
- On first run, the script opens a browser for the user to authorize access.

## Dependencies

```
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

## Usage

```bash
python search_attachments.py "from:boss@example.com"
```

## Example Output

```
Found 3 emails matching "from:boss@example.com" with attachments:

1. 2026-04-30  From: boss@example.com  Subject: Q1 Report
   Attachments: q1_report.pdf

2. 2026-03-15  From: boss@example.com  Subject: Contract Draft
   Attachments: contract_v2.docx, nda.pdf

3. 2026-02-01  From: boss@example.com  Subject: Budget Spreadsheet
   Attachments: budget_2026.xlsx
```

## Error Handling

- Missing `credentials.json`: print a clear error message explaining where to obtain the file.
- Gmail API errors: surface the error message and exit with a non-zero status code.
- No results: print `"No emails with attachments found for query: <query>"` and exit 0.

## Out of Scope

- Downloading attachment contents.
- Pagination beyond the first API response page (Gmail returns up to 100 results per page; 3 results will always fit in the first page).
- Support for multiple Gmail accounts.
