---
goal: Python CLI script to search Gmail and list emails with attachments
prompt:
  Create a simple Python script that searches Gmail for emails matching a user-provided query, then
  returns the last 3 matching emails that have attachments.
complexity: 5
---

## Success Criteria

- Script accepts a Gmail search query as a CLI argument (e.g. `python search_gmail.py "from:boss"`)
- Authenticates via OAuth2 using a `credentials.json` from Google Cloud Console; caches the token to
  `token.json` after first browser approval
- Appends `has:attachment` to the user query before calling the Gmail API, ensuring only emails with
  attachments are matched
- Retrieves the 3 most recent matching emails (Gmail API returns results newest-first)
- For each matched email, prints: subject, sender, date, and attachment filenames with file sizes
- Gracefully handles the case where fewer than 3 emails match
- Uses read-only OAuth scope (`gmail.readonly`) — no write access requested

## Out of Scope

- Downloading or saving attachment files to disk
- Sending email, modifying labels, or any write operations
- Pagination past the first API result page (first 100 results is sufficient for an interactive
  tool)
- Unit tests or CI setup
- GUI, web interface, or packaging as a library

## Risks and Assumptions

- **Google Cloud project required**: The user must create a Google Cloud project, enable the Gmail
  API, and download `credentials.json`. The script will print a clear error and setup hint if the
  file is missing.
- **Result ordering**: "Last 3" means the 3 most recent; this matches Gmail API default ordering
  (newest first), so no extra sorting is needed.
- **Attachment detection strategy**: Adding `has:attachment` to the query at the API level is
  simpler and more efficient than post-filtering by inspecting MIME parts. This is the chosen
  approach; the user's own query terms are preserved alongside it.
- **Token refresh**: `google-auth-oauthlib` handles token refresh automatically; expired tokens are
  renewed without re-opening the browser.
- **Rate limits**: Not a concern for a single interactive query.

## Implementation Plan

### 1. Project files

- `search_gmail.py` — main script
- `requirements.txt` — `google-auth-oauthlib`, `google-api-python-client`

### 2. OAuth2 authentication helper

- Load `credentials.json`; check for cached `token.json`
- On first run, open browser for user consent using scope `gmail.readonly`
- Save refreshed credentials back to `token.json`

### 3. CLI argument parsing with `argparse`

- Required positional argument: `query` (the Gmail search string)
- Print usage hint if called with no arguments

### 4. Gmail API search

- Build a Gmail API service object
- Call `users.messages.list` with combined query `(<user_query>) has:attachment`
- Limit to first page, take up to 3 message IDs

### 5. Fetch and display email details

- For each message ID, call `users.messages.get` with `format=full`
- Parse headers: `Subject`, `From`, `Date`
- Walk MIME payload parts to collect attachment `filename` and `size`
- Print a clean summary block per email
