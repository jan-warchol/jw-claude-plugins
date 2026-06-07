# Gmail Attachment Search Script

## Goal

Provide a quick command-line tool for finding emails with attachments that match a Gmail search
query. The motivation is to let users locate relevant attachments without leaving the terminal —
useful when they remember something about an email (sender, subject keyword, date range) but not
the exact attachment name.

## Requirements

- Accepts a Gmail search query string as a CLI argument (same syntax as the Gmail search bar).
- Searches the user's Gmail account and returns the **3 most recent** matching emails that contain
  at least one attachment.
- For each matching email, prints to stdout:
  - Date, sender, and subject
  - For each attachment: filename and size
- Output is human-readable plain text; no files are saved or downloaded.
- Exits with a non-zero code and a clear error message if authentication fails, the query returns
  no results, or fewer than 3 matches with attachments exist (partial results are still printed).
- Authentication uses the standard Google OAuth2 flow (`credentials.json` + cached token). On
  first run the user is directed to a browser to authorize; the token is cached locally for
  subsequent runs.

**Out of scope:**

- Downloading or saving attachments
- Interactive query building
- Handling more than 3 results

## Solution

Use the **Gmail API** via the `google-api-python-client` library (the standard, well-documented
path for OAuth2-authenticated access).

### Approach

1. Load `credentials.json` from the working directory; perform OAuth2 flow if no cached token
   exists (token stored as `token.json`).
2. Issue a `users.messages.list` request with the user's query plus the implicit filter
   `has:attachment`. Gmail's API returns results newest-first by default.
3. Fetch full message details (`format=metadata`, requesting `From`, `Date`, `Subject` headers
   plus the `parts` payload structure) for each result, stopping once 3 messages with attachments
   are confirmed.
4. Extract attachment metadata (filename, size in bytes) from `payload.parts`, recursing into
   nested `multipart/*` parts as needed.
5. Print results to stdout.

### Key design choices

- **`format=metadata`** avoids downloading message bodies/attachment data, keeping the script fast
  and the required OAuth scope minimal (`gmail.readonly`).
- Attachment detection via the API's `has:attachment` query modifier is done at search time,
  avoiding the need to post-filter results.
- No external config file — `credentials.json` and `token.json` are expected in the current
  working directory (standard convention for Google API quickstart scripts).
- Dependencies: `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`.

## Unknowns

- **`credentials.json` setup**: the user must create a Google Cloud project and download OAuth2
  credentials themselves. The script should print a clear one-line pointer to the setup docs on
  first use if the file is missing.
- **Quota**: Gmail API has a daily quota (1 billion units). A single run of this script costs on
  the order of a few hundred units — not a practical concern for interactive use.
- **Inline attachments**: some emails embed images as `inline` content-disposition parts. Whether
  to list these alongside regular attachments is unspecified; the simplest approach is to include
  all `filename`-bearing parts regardless of disposition.
