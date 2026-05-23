# Gmail Attachment Search Script

## Overview

Single-file Python CLI script: searches Gmail for emails matching a user query and prints the 3 most recent results that have attachments.

## Functional Requirements

- Accept a search query as a CLI argument; auto-append `has:attachment` before querying the API.
- Return up to 3 results sorted by date descending; print a message if none found.
- For each result, print: subject (fallback `"(no subject)"`), sender, date (`YYYY-MM-DD`), and filenames of `Content-Disposition: attachment` parts (inline images excluded).

## Authentication

- OAuth 2.0 with `credentials.json` from Google Cloud Console; scope `gmail.readonly`.
- Cache token in `token.json`; open browser for first-run authorization; auto-refresh on expiry.
- Prerequisite: Gmail API enabled in a Google Cloud project, `credentials.json` in the working directory.
- Trash and Spam excluded (Gmail API default).

## Non-Functional Requirements

- Single Python file; dependencies: `google-auth`, `google-auth-oauthlib`, `google-api-python-client`.
- On auth failure: print error and exit non-zero.

## Design Decisions

- **`has:attachment` auto-appended**: script's purpose is attachment search, so silently adding the filter is correct.
- **OAuth 2.0 over service account**: service accounts need domain-wide delegation, unavailable for personal Gmail.
- **Inline images excluded**: only `Content-Disposition: attachment` parts reported.

## Out of Scope

- Downloading attachments.
- Pagination beyond the first API result page.
- Multiple accounts or configurable result count.
