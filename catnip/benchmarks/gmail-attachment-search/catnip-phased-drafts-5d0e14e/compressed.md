# Gmail Attachment Search Script — Spec

## Overview

CLI Python script: given a Gmail search query, prints the 3 most recent matching emails with attachments.

## Inputs

- **Query** (positional): Gmail search syntax (e.g. `from:alice subject:invoice`).
- **`--credentials PATH`** (optional): path to `credentials.json`; default `./credentials.json`.

## Outputs

Up to 3 results, each a 4-line block:

```
Date:        2024-03-15 14:32 UTC
From:        alice@example.com
Subject:     Q1 Invoice
Attachments: invoice.pdf, receipt.png
```

No matches → `No emails found matching query.` (exit 0).

## Behavior

1. Authenticate via OAuth 2.0 (token reused across runs).
2. Append `has:attachment` to query unless already present (substring check).
3. Request first 3 results from the API (newest-first by default).
4. For each: extract `Date`, `From`, `Subject` headers and non-empty attachment filenames from `parts`.
5. Print to stdout.

## Authentication

Uses `google-auth` / `google-api-python-client`. First run: browser OAuth, token saved to `~/.config/gmail-search/token.json`. Scope: `gmail.readonly`.

## Error Handling

- Missing/invalid credentials: message with setup instructions, exit non-zero.
- Network/API errors: print error, exit non-zero.
- No query: print usage, exit non-zero.

## Design Choices

Gmail API (not IMAP) gives structured attachment metadata without parsing raw MIME. Result limit of 3 is hardcoded; no `--count` flag.

## Assumptions and Risks

- User has a GCP project with Gmail API enabled and `credentials.json` ready.
- Browser required for initial OAuth; headless unsupported.
- No retry logic for transient quota errors.

## Dependencies

Python 3.9+, `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`

## Out of Scope

Downloading attachments, pagination, email modification, GUI, configurable count.
