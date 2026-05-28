# Spec: Gmail Attachment Search Script

## Objective

Build a simple Python CLI script that authenticates with Gmail, accepts a user-provided search query, and returns the 3 most recent emails matching that query that also have at least one attachment. The script lets users quickly locate recent attachments in their inbox without opening a browser.

## Requirements

**Must do:**
- Accept a Gmail search query string from the user (via CLI argument or interactive prompt)
- Authenticate with the user's Gmail account using OAuth2
- Search Gmail using the provided query, restricted to messages that have attachments
- Return the 3 most recent matching emails
- Display for each result: subject, sender, date, and the names (and ideally sizes) of attachments
- Cache the OAuth token locally so the user is not re-prompted on subsequent runs

**Must not:**
- Download attachment content (display metadata only)
- Modify, move, or delete any emails
- Store or transmit credentials beyond what Google's OAuth2 flow requires

## Solution

**Authentication:** Use `google-auth-oauthlib` + `google-api-python-client` with a `credentials.json` file obtained from the Google Cloud Console. On first run, open a browser for the OAuth2 consent flow and persist the token to `token.json` in the working directory.

**Search:** Call `gmail.users().messages().list()` with `q=<user_query> has:attachment` and `maxResults=3`. Gmail's API returns results sorted newest-first by default, so the first 3 results are the most recent.

**Detail fetch:** For each of the 3 message IDs, call `gmail.users().messages().get()` with `format=metadata` and fetch headers (`Subject`, `From`, `Date`) plus the `payload.parts` tree to extract attachment filenames and sizes.

**Output:** Print results to stdout as plain text, one email per block, with a separator line between results.

**Dependencies:**
- `google-api-python-client`
- `google-auth-oauthlib`
- `google-auth-httplib2`

**Entry point:** `gmail_search.py`, run as `python gmail_search.py "<query>"`.

## Alternative solutions considered

- **`imaplib` (IMAP):** Avoids the Google Cloud Console setup but requires enabling "Less secure app access" or app passwords, which Google is phasing out. Gmail API is the correct modern approach.
- **`simplegmail` / third-party wrappers:** Reduce boilerplate but add an opaque dependency. The official client library is thin enough that direct use is simpler for a small script.

## Out of scope

- Downloading or saving attachment files
- Pagination beyond the first 3 results
- Support for multiple Gmail accounts simultaneously
- Sending emails or any write operations
- Packaging as an installable CLI tool

## Uncertainty

- **Assumption — OAuth credentials setup:** The user is expected to create a project in Google Cloud Console, enable the Gmail API, and download `credentials.json`. The script should print clear instructions if the file is missing, but the setup itself is out of scope.
- **Assumption — "returns" means prints to stdout:** No file output or structured data format (JSON, CSV) is implied unless the user later requests it.
- **Assumption — "last 3" means newest by received date:** Gmail's default sort order (newest first) is used; no secondary sort is applied.
- **Query combining:** Appending `has:attachment` to the user's query could conflict with a query that already includes `has:attachment` or uses `-has:attachment`. This should be handled gracefully (e.g., check before appending, or just let Gmail deduplicate it — Gmail handles duplicate `has:attachment` clauses without error).
- **Token expiry / revocation:** The script should handle `google.auth.exceptions.RefreshError` and prompt re-authentication instead of crashing.
