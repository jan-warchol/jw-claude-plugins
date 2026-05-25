# Gmail Attachment Search Script — Spec

## Overview

A single-file Python CLI that authenticates with Gmail and returns the 3 most recent emails matching a user query that also have attachments.

---

## Functional Requirements

**Input:** One positional argument — a Gmail search query string (standard Gmail operators).

**Processing:**
- Authenticate via OAuth 2.0 (`gmail.readonly` scope).
- Append `has:attachment` to the query; retrieve up to 3 results, newest first.

**Output** (stdout, blank line between entries):
- Date (`YYYY-MM-DD`), sender, subject, attachment filenames.

If no results: print `No emails found matching the query.`, exit 0.  
On auth/API error: print descriptive message to stderr, exit non-zero.

---

## Authentication

- OAuth 2.0; cached in `token.json` (browser auth only on first run).
- `credentials.json` read from working directory or `$GMAIL_CREDENTIALS`.

---

## Non-Functional Requirements

- Single `.py` file; dependencies: `google-auth`, `google-auth-oauthlib`, `google-api-python-client`.
- Filenames only — no attachment downloading.
- Return fewer than 3 if fewer exist; no error.

---

## Design Notes

- Fixed count of 3 keeps output minimal; `--count` flag deferred.
- OAuth 2.0 preferred over service accounts (no domain delegation needed).
- No pagination — API default page (≤100) is sufficient to find 3 matches.

---

## Out of Scope

Downloading attachments, pagination, multiple accounts, interactive query input, email body text.
