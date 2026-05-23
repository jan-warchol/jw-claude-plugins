# Gmail Attachment Search Script — Spec

## Goal

A command-line Python script that searches a user's Gmail inbox for emails matching a given query and returns the 3 most recent matching emails that have at least one attachment.

## Inputs

- **Query string** (required, positional CLI argument): A Gmail search query (e.g. `"from:boss@company.com"`, `"subject:invoice"`). Passed exactly as the user types it.

## Outputs

Prints to stdout a summary of up to 3 matching emails, one per block, including:
- Date received
- Sender (`From:`)
- Subject
- List of attachment filenames

## Behavior

1. Authenticate with Gmail using OAuth 2.0 (credentials stored in `credentials.json`; token cached in `token.json` after first login).
2. Search Gmail with the user's query **plus** the implicit filter `has:attachment` appended automatically.
3. Retrieve results ordered by most recent first (Gmail default).
4. Fetch full message details for up to the first 3 results.
5. For each message, extract and display the metadata listed above.
6. If fewer than 3 matching emails exist, display however many were found.
7. If no matching emails exist, print a clear "No results found." message and exit 0.

## Authentication

- Uses the Gmail API via `google-api-python-client` and `google-auth-oauthlib`.
- On first run, opens a browser for OAuth consent; subsequent runs use the cached token.
- Required OAuth scope: `https://www.googleapis.com/auth/gmail.readonly`.

## Error Handling

- Missing `credentials.json`: print an actionable error message explaining how to obtain it, then exit 1.
- Gmail API errors: surface the error message and exit 1.
- No query argument provided: print usage instructions and exit 1.

## Non-Goals

- Downloading attachment files to disk.
- Pagination beyond the first 3 results.
- Modifying, labeling, or deleting messages.
- Support for multiple Gmail accounts.

## Dependencies

- Python 3.8+
- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

## File Layout

```
gmail_attachment_search.py   # main script
credentials.json             # OAuth client secret (user-provided, gitignored)
token.json                   # cached token (auto-generated, gitignored)
requirements.txt             # pinned dependencies
```
