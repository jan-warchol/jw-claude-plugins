# Gmail Attachment Search Script

## Goal

A CLI Python script that accepts a Gmail search query, finds the 3 most recent matching emails
containing attachments, and prints their metadata to stdout.

## Requirements

- Accept a search query string as a CLI argument
- Authenticate with Gmail using a local OAuth2 credentials file
- Return the 3 most recent emails matching the query that have attachments (fewer if fewer match)
- Print per email: subject, sender, date, attachment filenames
- Exit with a clear error message on auth failure, API error, or no matches

**Out of scope:** downloading attachments, pagination beyond 3 results.

## Design

- Dependencies: `google-api-python-client`, `google-auth-oauthlib`
- Auth: load `credentials.json` from working directory; persist token in `token.json`; trigger
  browser OAuth flow on first use
- Query: append `has:attachment` to the user-provided query before calling `users.messages.list`
- Fetch only headers (Subject, From, Date) and MIME part metadata to extract attachment filenames
  — no body/attachment data downloaded
- Output: plain text, one block per email

## Unknowns

**Assumptions:**

- User has a Google Cloud project with Gmail API enabled and a valid `credentials.json` OAuth2
  client secrets file
- Python 3.8+
- "Most recent" = Gmail API default ordering by `internalDate` descending
- Inline attachments (Content-Disposition: inline) count as attachments
