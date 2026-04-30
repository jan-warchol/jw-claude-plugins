---
goal: Python script searching Gmail for emails with attachments
prompt: Create a simple Python script that searches Gmail for emails matching a user-provided query, then returns the last 3 matching emails that have attachments.
complexity: 4
---

## Overview

A standalone Python script that accepts a search query, authenticates with Gmail via OAuth2, and prints metadata for the 3 most recent matching emails that have attachments.

## Success Criteria

- Script accepts a search query as a CLI argument (or interactive prompt if omitted)
- Authenticates with Gmail API using OAuth2; stores token in a local file for reuse on subsequent runs
- Fetches emails matching the query, filtered to only those with attachments
- Returns exactly the 3 most recent matching emails (or fewer if fewer exist)
- For each email, prints: subject, sender, date, and attachment filenames
- Handles gracefully when fewer than 3 matches are found

## Non-Goals

- Downloading or saving attachment files to disk
- Sending, modifying, or deleting emails
- Supporting email providers other than Gmail
- Building a GUI or web interface
- Automating Google Cloud project setup (user provides `credentials.json` manually)

## Implementation Steps

1. **Dependencies** — use `google-auth-oauthlib` and `google-api-python-client`; include a `requirements.txt`
2. **Auth flow** — load `credentials.json`, run OAuth2 consent flow on first run, cache token in `token.json` for reuse
3. **Search** — call `users.messages.list` with the user's query plus `has:attachment` appended; request only the most recent results
4. **Fetch details** — for each result call `users.messages.get` with `format=metadata` to retrieve headers (Subject, From, Date) and MIME part names for attachments
5. **Output** — print subject, sender, date, and attachment filenames for the top 3 results in a readable format
