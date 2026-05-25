# Gmail Attachment Search Script — Spec

## Goal

CLI Python script that searches Gmail for emails matching a query and returns the 3 most recent with at least one attachment.

## Inputs

- **Query string** (required, positional): A Gmail search query (e.g. `"from:boss@company.com"`).

## Outputs

Prints up to 3 matching emails to stdout, one block each, separated by blank lines:
- Date received (`Date:` header)
- Sender (`From:` header, including display name)
- Subject (`(no subject)` if absent or empty)
- Attachment filenames, one per line (`(unnamed)` if no filename)

## Behavior

1. Authenticate via OAuth 2.0 (`credentials.json`; token cached in `token.json`).
2. Search with user's query plus implicit `has:attachment` appended automatically.
3. Fetch full details for up to the first 3 results (most recent first).
4. Attachments are MIME parts with `Content-Disposition: attachment` or a `filename` parameter on any `Content-Type` header.
5. If fewer than 3 results, show what was found. If none, print `"No results found."` and exit 0.

## Authentication

- Uses `google-api-python-client` and `google-auth-oauthlib`.
- First run opens a browser for OAuth consent; expired tokens auto-refresh; on failure, re-prompts.
- Scope: `https://www.googleapis.com/auth/gmail.readonly`.
- `token.json` is gitignored.

## Error Handling

- Missing `credentials.json`: actionable error explaining how to obtain it, exit 1.
- Gmail API errors: surface the message, exit 1.
- No query argument: print usage, exit 1.

## Non-Goals

Downloading attachments, pagination, message modification, multiple accounts, JSON output.

## Dependencies

Python 3.8+, `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`

## Files

```
gmail_attachment_search.py   # main script
credentials.json             # OAuth client secret (user-provided, gitignored)
token.json                   # cached token (auto-generated, gitignored)
requirements.txt
```
