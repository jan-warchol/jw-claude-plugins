# Spec: Gmail Attachment Search Script

## Overview

CLI Python script that searches a Gmail mailbox via a user-supplied query and prints the three most recently received matching emails with non-inline attachments.

## Behavior

### Input
Single positional argument: a Gmail search query (e.g., `"from:boss@example.com subject:report"`). The script appends `has:attachment` automatically; users omit it.

### Processing
1. Authenticate via OAuth 2.0.
2. Call `messages.list` with `<user-query> has:attachment` (results are reverse-chronological by default).
3. Take the first three message IDs.
4. Fetch each with `messages.get format=metadata` to retrieve headers and part descriptors.

### Output
Plain text per email: `From`, `Subject`, `Date`, and a list of attachment filenames + MIME types.

Only parts with a non-empty `filename` and `Content-Disposition: attachment` qualify; inline images are excluded.

Print fewer than three results if fewer match; print an informative message (exit 0) if none match.

## Setup

Requires Python 3.8+.

| Package | Purpose |
|---|---|
| `google-api-python-client` | Gmail API wrapper |
| `google-auth-oauthlib` | OAuth 2.0 flow |
| `google-auth-httplib2` | HTTP transport |

```
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
```

**Auth:** credentials are read from `credentials.json` in the working directory (from Google Cloud Console). First run opens a browser for OAuth consent; the token is cached in `token.json` and refreshed automatically. Scope: `gmail.readonly`.

*Service-account alternative rejected:* requires domain-wide delegation (Workspace only); OAuth 2.0 works for all Gmail accounts.

## Error Handling

| Condition | Action |
|---|---|
| Missing `credentials.json` | Print setup instructions, exit 1 |
| No query argument | Print usage, exit 1 |
| API error (network/quota/permissions) | Print error, exit 1 |
| Expired/revoked token | Instruct user to delete `token.json` and re-run |

## Constraints and Non-Goals

**Assumptions:** user has a GCP project with Gmail API enabled and `credentials.json` downloaded. Invalid queries silently return zero results (no local validation).

**Out of scope:** downloading attachment content; sending or modifying emails; pagination past the first API page (≤500 results; sufficient for top 3); GUI.
