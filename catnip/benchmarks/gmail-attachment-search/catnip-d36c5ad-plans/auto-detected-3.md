---
goal: Python script to find last 3 Gmail emails with attachments
prompt: Create a simple Python script that searches Gmail for emails matching a user-provided query, then returns the last 3 matching emails that have attachments.
complexity: 3
---

## Success Criteria

- Script accepts a search query string as a CLI argument
- Authenticates with Gmail via OAuth2 using a local `credentials.json` file; tokens are cached in `token.json` after first login
- Searches Gmail with the given query, filtered to messages that have attachments (`has:attachment` appended automatically)
- Returns the 3 most recent matching emails, printing subject, sender, date, and attachment filenames for each
- Graceful error message if fewer than 3 matches are found

## Out of Scope

- Downloading or saving attachment files locally
- Sending or modifying emails
- Support for multiple Gmail accounts
- Pagination beyond the first result page

## Implementation Steps

1. Set up project: `requirements.txt` with `google-api-python-client`, `google-auth-oauthlib`
2. Implement OAuth2 flow using `InstalledAppFlow` with `gmail.readonly` scope; cache token to `token.json`
3. Build Gmail API query: combine user-supplied query with `has:attachment`, call `messages.list` with `maxResults=3`
4. For each message ID, call `messages.get` with `format=metadata` to extract headers (Subject, From, Date) and part filenames
5. Print formatted summary for each of the 3 results
