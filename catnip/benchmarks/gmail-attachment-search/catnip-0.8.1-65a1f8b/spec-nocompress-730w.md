# Gmail Attachment Search — Specification

## Goal

A command-line Python script that accepts a Gmail search query from the user, finds the three most
recent matching emails that contain at least one attachment, and prints a human-readable summary
of each email and its attachments to stdout.

## Behavior

### Invocation

The script is run from the terminal with the search query as a positional argument:

```
python gmail_attachments.py "from:boss@example.com"
```

### Authentication

- On first run the script opens a browser-based OAuth2 consent flow using the Gmail API.
- After the user grants access, the script stores the resulting token locally (e.g., `token.json`)
  so subsequent runs do not require re-authorization.
- If the stored token is expired the script refreshes it silently; if refresh fails it re-triggers
  the consent flow.
- The script reads OAuth2 client credentials from a `credentials.json` file in the working
  directory (standard Google Cloud Desktop App credential format).

### Search and filtering

- The script passes the user-provided query string verbatim to the Gmail API `messages.list`
  endpoint (same syntax as the Gmail search bar).
- From the results it selects only messages that have at least one attachment (i.e., at least one
  message part whose `filename` is non-empty and whose body has a non-zero `size`).
- It returns the **three most recent** qualifying messages (ordered by Gmail's default
  relevance/date ordering, newest first).
- If fewer than three qualifying messages exist, the script prints however many were found and
  notes this in its output.
- If no qualifying messages exist, the script prints an informative message and exits with code 0.

### Output format

For each of the (up to) three emails the script prints a block like:

```
────────────────────────────────────────
Subject : Weekly report
From    : boss@example.com
Date    : 2026-06-03 14:22 UTC
Snippet : Please find this week's numbers attached...

Attachments (2):
  • report.xlsx   (48 KB)
  • notes.pdf     (112 KB)
```

Blocks are separated by a horizontal rule. No attachments are downloaded.

### Error handling

- Missing or invalid `credentials.json`: print a clear error message explaining where to obtain
  credentials; exit with code 1.
- Gmail API errors (rate limits, network failures): print the error and exit with code 1.
- Invalid or empty query string: print usage hint and exit with code 1.

## Solution

### Language and dependencies

- Python 3.9+
- `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib` (standard Google
  client libraries)
- No other third-party dependencies

### Gmail API usage

- Scope: `https://www.googleapis.com/auth/gmail.readonly` (read-only; sufficient for listing and
  fetching message metadata).
- Search: `users.messages.list` with the `q` parameter set to the user's query and `maxResults`
  set to a reasonable page size (e.g. 20) to avoid fetching more than needed.
- Message fetch: `users.messages.get` with `format=full` to retrieve headers and MIME part
  metadata. Body data (actual attachment bytes) is not fetched.
- Attachment detection: iterate over `payload.parts` recursively; a part is considered an
  attachment when `part['filename']` is non-empty and `part['body']['size'] > 0`.

### Design choices

- **Verbatim query passthrough**: the script does not parse or modify the query, letting Gmail
  handle all search semantics (labels, operators, date filters, etc.).
- **No download**: downloading attachments is out of scope to keep the script minimal and avoid
  requiring user decisions about save paths and overwrite behavior.
- **`format=full` over `format=metadata`**: `metadata` would suffice for headers but does not
  expose MIME part filenames reliably; `full` is used to allow accurate attachment detection.
- **Three results hard-coded**: the count is fixed rather than configurable to keep the CLI
  interface simple. A `--count` flag was considered and deferred.
- **Token stored as `token.json`**: follows the standard pattern from Google's own Python
  quickstart examples, so existing documentation applies directly.

## Unknowns

- **Inline images**: some emails embed images as MIME attachments (e.g., signatures). These will
  be counted as attachments by the detection logic above. Whether this is desirable depends on the
  user's intent and is not addressed here.
- **Very large result sets**: if the query matches thousands of messages with few attachments, the
  script may need to fetch multiple pages from the API before finding three qualifying messages.
  The current design does not cap total API calls; a page limit could be added if latency becomes
  a concern.
- **Token storage location**: `token.json` is placed in the working directory, which may be
  undesirable if the script is installed system-wide. A `~/.config/` path was not chosen to avoid
  complexity; this can be revisited.
