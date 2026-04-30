---
goal: Search Gmail and return 3 latest emails with attachments
prompt: Create a simple Python script that searches Gmail for emails matching a user-provided query, then returns the last 3 matching emails that have attachments.
complexity: 3
---

### Success Criteria

- Script accepts a search query string as a command-line argument
- Authenticates with Gmail via OAuth2, with inline setup instructions for creating credentials in Google Cloud Console
- Returns the 3 most recent emails matching the query that contain at least one attachment
- Displays subject, sender, date, and attachment filenames for each result

### Out of Scope

- Downloading or saving attachment file contents
- Sending emails or modifying Gmail state
- Support for multiple Gmail accounts
- Pagination beyond the first page of results

### Implementation Steps

1. **Setup guide**: Include comments in the script documenting how to create OAuth2 credentials in Google Cloud Console and enable the Gmail API
2. **Authentication**: Use `google-auth-oauthlib` to handle the OAuth2 flow, storing tokens in a local `token.json` file for reuse
3. **Search**: Call `gmail.users.messages.list` with the user's query plus `has:attachment` appended to filter out attachment-free results
4. **Fetch details**: For the top 3 results, call `gmail.users.messages.get` to retrieve headers (Subject, From, Date) and MIME part metadata for attachment filenames
5. **Output**: Print each email's subject, sender, date, and list of attachment filenames to stdout
