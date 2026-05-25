# Gmail Attachment Search Script

## Goal

Create a Python CLI script that accepts a user-provided search query, searches the
authenticated user's Gmail inbox, and returns the 3 most recent matching emails that
have attachments — printing for each: date received, sender, subject, and attachment
filenames.

## Requirements

The following criteria must all be satisfied for the implementation to be considered
complete:

1. The script accepts a search query as a CLI argument (via `argparse`); if no argument
   is provided, it prompts the user interactively.
2. It returns up to 3 emails matching the query that contain attachments, sorted
   newest-first; if fewer than 3 exist, it returns however many are found.
3. For each result it prints: date received, sender (`From` header), subject, and the
   list of attachment filenames.
4. When no matching emails are found, it prints an informative message and exits with
   code 0.
5. When `credentials.json` is missing, it prints a message explaining how to obtain
   the file (pointing to Google Cloud Console) and exits with code 1.
6. On Gmail API or network errors, it catches `HttpError`, prints the error message,
   and exits with code 1.
7. On first run, a browser-based OAuth consent flow opens and the resulting token is
   saved to `token.json`; on subsequent runs the cached token is reused and refreshed
   automatically on expiry.

## Solution

### Approach

Use the Gmail API (v1) via `google-api-python-client` with OAuth 2.0 authentication
through `google-auth-oauthlib`. Before issuing the API search call, append
`has:attachment` to the user's query so that attachment filtering is done server-side
by Gmail. Pass `maxResults=3` to the API to limit the result count server-side — not
by fetching a larger set and truncating client-side. Then fetch full message details
for each of the (up to) 3 results to extract headers and attachment filenames.

### Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| OAuth scope | `gmail.readonly` | Minimum privilege — the script never modifies or sends email |
| Attachment filtering | `has:attachment` appended server-side | More efficient than client-side filtering; reduces API calls and quota usage |
| Result limit | `maxResults=3` via API parameter | Server-side cap; 3 results always fit in the first response page, no pagination needed |
| Token storage | `token.json` in working directory | Standard desktop OAuth pattern; avoids re-authorization on every run |
| Output | Plain text to stdout | No extra dependencies; trivially pipeable and redirectable |

### Alternatives Considered

- **Service account authentication**: rejected — service accounts cannot access a
  personal Gmail inbox without domain-wide delegation, which is not available on
  personal Google accounts.
- **Client-side attachment filtering**: rejected — would require fetching many
  results and discarding most. `has:attachment` is a first-class Gmail search
  operator; filtering server-side is both simpler and more efficient.
- **`maxResults` buffer (e.g., fetch 10, display 3)**: rejected — adds complexity
  with no benefit. Because `has:attachment` is applied server-side, every returned
  result is guaranteed to have an attachment; a buffer is unnecessary.

## Setup Prerequisites

The following one-time manual setup in Google Cloud Console is required before first
use:

1. Go to [Google Cloud Console](https://console.cloud.google.com/) and create or
   select a project.
2. Enable the **Gmail API** for the project.
3. Create **OAuth 2.0 credentials** of type **Desktop App**.
4. Download the resulting `credentials.json` file and place it in the script's working
   directory.
5. Add both `credentials.json` and `token.json` to `.gitignore` — neither should ever
   be committed to version control.

## Dependencies

```
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

CLI argument parsing uses Python's built-in `argparse` module (no additional
dependency).

## Out of Scope

- **Downloading attachment content**: only filenames are listed; file data is never
  fetched.
- **Pagination**: with `maxResults=3` all results fit in the first API response page;
  pagination is not required.
- **Multiple Gmail accounts simultaneously**: a single authenticated user only.
- **Sending, modifying, labelling, or deleting emails**: the `gmail.readonly` scope
  makes these impossible.
- **GUI or web interface**: CLI only.

## Risks, Assumptions, and Open Questions

### Assumptions

- The user has a Google account and can access Google Cloud Console to create OAuth
  credentials.
- Gmail's default result ordering (newest-first) is reliable for the purposes of
  returning the 3 most recent results; no explicit sort parameter is needed.
- Three results always fit within the first API response page when `maxResults=3` is
  set, so no pagination logic is needed.

### Risks

- **Token refresh failure**: if `token.json` is corrupted or the OAuth refresh token
  has been revoked by the user, automatic refresh will fail. The script should detect
  this, delete the invalid token, and re-run the browser consent flow.
- **Gmail indexing lag**: `has:attachment` relies on Gmail's search index, which
  occasionally lags. A recently received email with an attachment may temporarily not
  appear in results; this is a known Gmail API limitation with no workaround.
- **Stale credentials file**: if the OAuth client is deleted or reset in Google Cloud
  Console, the local `credentials.json` becomes invalid and the user must repeat the
  setup steps.

### Open Questions

- Should attachment MIME types be included in the output alongside filenames? More
  informative but adds verbosity; could be an opt-in flag.
- Should the script support a configurable result count (e.g., `--count N`) rather
  than a hard-coded 3?
