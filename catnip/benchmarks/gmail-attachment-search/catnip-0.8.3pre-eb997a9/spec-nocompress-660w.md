# Specification: Gmail Attachment Search Script

## Goal

Provide a simple Python script that searches a user's Gmail for emails matching a user-supplied
query and reports the 3 most recent matching emails **that have attachments**.

## Requirements

### Behavior

- Accept a Gmail search query as a command-line argument.
- Search the authenticated user's mailbox using that query.
- Restrict results to emails that have at least one attachment.
- Return the 3 most recent such emails (newest first). If fewer than 3 match, return all that
  match.
- For each returned email, print to the console:
  - sender
  - subject
  - date
  - attachment filename(s)
- Attachment-only filter applies to real file attachments, not inline images embedded in the
  message body (see Assumptions).

### Out of scope

- Downloading or saving attachment contents (metadata only).
- Reading/printing email bodies.
- Modifying the mailbox (no labeling, deleting, marking read).
- Any GUI, interactive prompt, or persistent service.
- Pagination or returning more than 3 results.

### Success / failure criteria

- Success: given a query that matches ≥1 email with attachments, the script prints up to 3 emails
  newest-first, each showing the four fields above, and exits 0.
- A query with no matching attachment-bearing emails prints a clear "no results" message and
  exits 0.
- Authentication, network, or API errors print a readable message to stderr and exit non-zero — no
  raw tracebacks for expected failure modes.
- Missing/invalid query argument prints usage and exits non-zero.

## Design

### Approach

- Use the official **Gmail API** with **OAuth2** user authentication via the
  `google-api-python-client`, `google-auth`, and `google-auth-oauthlib` libraries.
- Combine the user's query with Gmail's `has:attachment` operator so the attachment filter is
  applied server-side, e.g. effective query = `({user_query}) has:attachment`. This keeps the
  result set small and lets the API do the filtering and ordering.
- Gmail's `messages.list` already returns newest-first, so take the first 3 ids (`maxResults=3`)
  and fetch each with `messages.get`.
- Parse the message `format=metadata` (or `full`) payload to extract `From`, `Subject`, `Date`
  headers and walk MIME parts for those with a `filename` to collect attachment names.

### Authentication / setup

- Requires a Google Cloud project with the Gmail API enabled and an OAuth client credentials file
  (`credentials.json`) placed next to the script.
- On first run, opens a browser consent flow and caches the resulting token (`token.json`) for
  subsequent runs.
- Uses the read-only scope `https://www.googleapis.com/auth/gmail.readonly`.

### Key choices / trade-offs

- **Server-side `has:attachment`** over client-side filtering: simpler and avoids
  fetching/inspecting many non-matching messages. Trade-off: relies on Gmail's own notion of
  "attachment" (see Assumptions).
- **Read-only scope**: principle of least privilege; the task never writes.
- **Metadata fetch format**: cheaper than `full`; sufficient for headers and the MIME part
  structure needed to read filenames.

### Rejected alternatives

- IMAP (`imaplib`): simpler auth but weaker/inconsistent search and no native `has:attachment`;
  rejected per chosen Gmail-API approach.
- MCP Gmail tools: not a standalone runnable script as requested.

## Unknowns

### Assumptions

- The user has, or can create, a Google Cloud project and obtain `credentials.json`; environment
  has a browser available for the consent flow.
- "Last 3" means the 3 most recently received matching emails.
- Gmail's `has:attachment` semantics define what counts as an attachment; inline images may or may
  not be included by Gmail — the script defers to the API and does not re-classify. If stricter
  exclusion of inline content is needed, it can be added by checking
  `Content-Disposition: attachment` on parts.
- Results are reported at the **message** level, not thread level (a thread with multiple matching
  messages may yield multiple entries).
- Standard internet access and an authenticated single Gmail account.

### Risks / open questions

- Token expiry/revocation requires re-consent; handled by refresh token, but a revoked token
  surfaces as an auth error.
- Very large attachments or unusual MIME structures could complicate filename extraction;
  mitigated by reading only header/part metadata.
- API rate limits are unlikely at this scale (≤3 message fetches per run).
