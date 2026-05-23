# Gmail Attachment Search Script

## Overview

A command-line Python script that searches across the user's entire Gmail account (not just the inbox folder) using a provided query string and returns the three most recent matching emails that contain attachments.

## Inputs

- A search query string passed as a command-line argument (e.g., `"from:boss subject:report"`), using Gmail's standard search syntax.

## Behavior

1. Authenticate with the Gmail API using OAuth 2.0, storing credentials locally for reuse across runs.
2. Search Gmail by combining the user's query with `has:attachment` server-side (e.g., `(user query) has:attachment`), so only emails Gmail considers to have attachments are returned. Inline images embedded in the message body are excluded by Gmail's own `has:attachment` definition.
3. Retrieve results sorted by date descending (Gmail API's default ordering); no client-side re-sorting is needed.
4. Fetch only message metadata (headers + MIME part structure) rather than full message bodies, to minimize API quota usage.
5. If fewer than three matching emails exist, return all that are found.
6. If no matching emails are found, print a clear message and exit with a non-zero status code.

## Output

For each matching email, print to stdout:

- Date received (from the `Date` header)
- Sender (`From` header)
- Subject line
- List of attachment filenames

Output is human-readable plain text. One blank line separates each email's block.

## Authentication

- Uses the Gmail API via `google-auth` and `google-api-python-client`.
- OAuth credentials are loaded from a `credentials.json` file in the working directory.
- The token is cached in `token.json` to avoid re-authentication on subsequent runs.
- If `token.json` is present but invalid or expired, it is deleted and the OAuth flow is re-triggered automatically.
- The OAuth flow opens a browser window on first run; this will fail in headless environments.
- Required OAuth scope: `https://www.googleapis.com/auth/gmail.readonly`.

## Error Handling

- Missing `credentials.json`: print an actionable error message explaining how to obtain credentials from Google Cloud Console.
- API errors (network, quota, permission): print the error message and exit with a non-zero status code.
- No query argument provided: print usage instructions and exit with a non-zero status code.

## Constraints and Exclusions

- Single-file script (`gmail_search.py`), no project scaffolding.
- No external dependencies beyond `google-auth-oauthlib`, `google-auth-httplib2`, and `google-api-python-client`.
- Read-only access; the script does not modify, delete, or send any emails.
- Lists attachment filenames only — does not download or save attachment content.
- Searches a single Gmail account; multi-account support is out of scope.
- Fetches only the first page of search results (up to 100 messages). Pagination is not implemented, which is sufficient for identifying the three most recent matches in nearly all cases.

## Design Choices and Alternatives

- **Gmail API over IMAP**: Avoids requiring the user to enable IMAP in Gmail settings and provides a quota-governed, reliable interface.
- **Server-side `has:attachment` filter**: Appending `has:attachment` to the user's query is more efficient than fetching all results and filtering client-side, and produces results consistent with what the user would see in the Gmail UI.
- **Metadata format**: Messages are fetched with `format=metadata` (headers + MIME structure) rather than `format=full`, reducing response size and API quota usage.

## Assumptions and Risks

- Assumes the user has a Google Cloud project with the Gmail API enabled and has downloaded `credentials.json` for a desktop OAuth client.
- Gmail API quota limits apply (250 units/user/second); no retry or back-off logic is implemented.
- Gmail's `has:attachment` may not match the user's intuition in edge cases (e.g., calendar invites, certain inline files).
