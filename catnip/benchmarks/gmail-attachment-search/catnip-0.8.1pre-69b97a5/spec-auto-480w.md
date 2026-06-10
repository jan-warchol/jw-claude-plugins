# Gmail Attachment Search — Specification

## 1. Purpose

A CLI Python script that accepts a Gmail search query and prints metadata for the 3 most recent
matching emails that contain attachments. Intended for quick, ad-hoc inspection of Gmail content
from the terminal.

---

## 2. Requirements

- **Input:** a single positional CLI argument — a Gmail search query string (e.g.
  `"from:boss invoice"`).
- **Filtering:** only emails that have at least one attachment are considered; emails without
  attachments are skipped.
- **Result count:** return the 3 most recent qualifying emails. If fewer than 3 exist, return all
  of them.
- **Output per email:**
  - Subject
  - Sender (`From` header)
  - Date
  - List of attachment filenames (name only, no download)
- Output is human-readable, printed to stdout.
- **No files are downloaded.**
- Authentication uses Gmail API + OAuth2; credentials persist across runs via a local token file.
- The script must handle auth errors (missing/expired token) gracefully with a clear message.
- No results found → print a clear message, exit 0.

---

## 3. Solution

### Approach

Use the [Gmail API](https://developers.google.com/gmail/api) via `google-api-python-client` and
`google-auth-oauthlib`.

### Authentication flow

- Requires a `credentials.json` (OAuth2 client secrets) in the working directory or a path set via
  env var `GMAIL_CREDENTIALS`.
- On first run, opens a browser for OAuth consent; token saved to `token.json` (same directory).
- Subsequent runs reuse the stored token, refreshing automatically.
- Required OAuth scope: `https://www.googleapis.com/auth/gmail.readonly`.

### Search & filtering

- Append `has:attachment` to the user-supplied query before calling `users.messages.list`, so
  Gmail itself pre-filters for attachments — avoids fetching messages without attachments.
- Fetch up to ~10 message IDs (to have a small buffer), ordered newest-first (default Gmail API
  order).
- For each message, retrieve the full payload (`format=full`) to inspect MIME parts and extract
  attachment filenames.
- Stop once 3 qualifying messages are collected.

### MIME parsing

- Iterate over `payload.parts` recursively; a part is an attachment if `filename` is non-empty or
  `Content-Disposition` is `attachment`.
- Collect all such filenames per message.

### CLI

- `argparse` with one positional argument `query`.
- Optional `--credentials` flag to override the default `credentials.json` path.

### Dependencies

- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

---

## 4. Uncertainty & Risks

- **`credentials.json` setup:** users must create a Google Cloud project and download OAuth
  credentials manually — not automatable. The script should print clear setup instructions if the
  file is missing.
- **Token security:** `token.json` is stored in plaintext; acceptable for a personal CLI tool but
  should be noted.
- **`has:attachment` accuracy:** Gmail's `has:attachment` filter is generally reliable but may
  occasionally miss inline attachments or count embedded images; edge cases are acceptable for
  this use case.
- **API quota:** Gmail API free tier (1 billion quota units/day) is far more than sufficient for
  this script.
- **Open question:** whether to support multiple output formats (e.g. JSON) in the future — out of
  scope for now.
