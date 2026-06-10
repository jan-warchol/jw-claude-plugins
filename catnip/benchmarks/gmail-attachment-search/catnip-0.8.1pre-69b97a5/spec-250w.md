# Gmail Attachment Search Script

## Purpose

A single-file Python CLI script that searches the user's Gmail account with a given query and
prints a summary of the 3 most recent matching emails that have attachments.

## Requirements

- Accept a single CLI argument: a Gmail search query string (Gmail search syntax)
- Automatically append `has:attachment` to the query to filter for emails with attachments
- Return the 3 most recent results; if fewer than 3 match, return all that do
- For each result, print to stdout: subject, sender (From), date, and list of attachment filenames
- Authenticate via OAuth2 using a `credentials.json` file in the working directory; cache tokens
  in `token.json`
- Prompt for browser-based re-authentication if token is expired or missing

## Design

- **Libraries**: `google-api-python-client`, `google-auth-oauthlib`
- **API calls**:
  - `users.messages.list` with the combined query to retrieve message IDs; paginate if needed to
    find 3 attachment emails
  - `users.messages.get` with `format=metadata` for subject/sender/date
  - Parse `payload.parts` recursively to extract attachment filenames (parts with non-empty
    `filename`)
- **Output**: plain text, one block per email; e.g. `Subject / From / Date / Attachments: [...]`
- Single script (`search_gmail.py`), no config beyond credential files
- Required OAuth scope: `https://www.googleapis.com/auth/gmail.readonly`

## Uncertainty

- If few emails match the query with attachments, multiple API result pages may be needed — the
  script should paginate up to ~50 messages scanned before stopping with whatever was found
- Users must enable the Gmail API and create OAuth credentials in Google Cloud Console before
  first use; the script should print a clear error if `credentials.json` is missing
