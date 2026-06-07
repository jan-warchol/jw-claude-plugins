# Gmail Attachment Search Script

## Goal

A standalone Python CLI script that accepts a Gmail search query from the user and prints a
human-readable summary of the last 3 matching emails that have at least one attachment.

## Requirements

- Accept a single positional argument: a Gmail search query string (same syntax as the Gmail
  search bar, e.g. `from:boss subject:report`).
- Filter results to only emails that contain at least one attachment.
- Return exactly the 3 most recent matching emails (or fewer if fewer than 3 exist).
- For each result, print: sender, subject, date, and the list of attachment filenames.
- Exit with a non-zero status and a clear error message on failure (auth error, API error, no
  results).
- Out of scope: downloading attachment files, pagination beyond the first result page, modifying
  emails, any GUI.

## Design

- **Auth**: OAuth2 via `google-auth-oauthlib` + `google-api-python-client`. On first run the
  script opens a browser for consent and saves a token to
  `~/.config/gmail-attachment-search/token.json`. Subsequent runs reuse the stored token,
  refreshing it automatically. A `credentials.json` (downloaded from Google Cloud Console) must
  exist in the same directory as the script or at a path supplied via `--credentials`.
- **Query strategy**: Send the user's query to the Gmail API `messages.list` endpoint. Use
  `maxResults=10` to fetch a small candidate page, then walk message details to find the first 3
  that have `parts` with a non-empty `filename`. This avoids fetching full message bodies
  unnecessarily.
- **Attachment detection**: A message has an attachment if any payload part has a non-empty
  `filename` field. No MIME-type guessing is needed.
- **Output**: Plain text, one block per email separated by a blank line:

  ```
  From:        Alice <alice@example.com>
  Subject:     Q1 Report
  Date:        2026-05-14 09:32
  Attachments: report.pdf, budget.xlsx
  ```

- **Dependencies**: `google-api-python-client`, `google-auth-oauthlib`. No other third-party
  libraries.

## Unknowns

- **Assumption**: The user already has (or will create) a Google Cloud project with the Gmail API
  enabled and a `credentials.json` OAuth client secret file. Setup instructions are out of scope
  for the spec but should be noted in the script's `--help` text.
- **Assumption**: 10 candidates is enough to find 3 with attachments for typical queries. If a
  query returns fewer than 3 results with attachments overall, the script prints what it finds and
  notes the count.
- **Risk**: Gmail API rate limits (250 quota units/user/second). Fetching metadata for up to 10
  messages individually is well within limits for a CLI tool, but could become a concern if the
  script is run in a tight loop.
- **Open question**: If the first page of 10 results contains fewer than 3 emails with
  attachments, should the script fetch the next page? For simplicity, the initial implementation
  will not paginate — this is a reasonable starting point and easy to extend later.
