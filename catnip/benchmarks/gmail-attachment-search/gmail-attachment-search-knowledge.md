=== TASK (complexity 3) === Create a simple Python script that searches Gmail for emails matching a
user-provided query, then returns the last 3 matching emails that have attachments. === TASK ===

=== USER ANSWERS === These questions were answered directly by a human user.

Q: How should the user provide the search query to the script?  
A: CLI arg with prompt fallback — accept the query as a command-line argument; if no argument is
given, prompt interactively via input().

Q: How should the script authenticate with Gmail?  
A: OAuth2 (user flow) — use google-auth-oauthlib with credentials.json + token.json caching; browser
consent on first run.

Q: What information should the script output for each matching email?  
A: Subject, sender, date, and attachment filenames. (No body/snippet; do not download attachment
contents.)

Q: What output format should the script produce?  
A: Human-readable text printed to stdout (one section per email).

Q: How should the script filter emails to only those with attachments?  
A: Append `has:attachment` to the user's query (server-side filter via Gmail search syntax).

Q: Where should OAuth credentials and token be stored?  
A: Same directory as the script — `credentials.json` and `token.json` next to the .py file.

Q: What should be included in the deliverable?  
A: A single Python script file, with inline setup-instruction comments at the top (no separate
README, no requirements.txt).

Q: How should errors (auth failure, network issues, no matches) be handled?  
A: Friendly error messages + non-zero exit codes for common error cases (auth failure, network/API
errors, no matches). === USER ANSWERS ===

=== PREPARED ANSWERS === These answers were prepared by AI agent in order to reduce ambiguity.

Q: Which Gmail API library?  
A: google-api-python-client + google-auth-oauthlib + google-auth-httplib2 (the standard
Google-recommended stack). Mention the pip install command in the inline setup comments.

Q: Which OAuth scope?  
A: `https://www.googleapis.com/auth/gmail.readonly` — read-only is sufficient since we only
list/read messages.

Q: What does "last 3" mean — sorted how?  
A: Gmail's `users.messages.list` returns results in reverse-chronological order by default (most
recent first). Take the first 3 results.

Q: How exactly to fetch each message's metadata?  
A: Call `users.messages.get` with `format='metadata'` and
`metadataHeaders=['Subject', 'From', 'Date']`. Iterate the message's payload parts to collect
attachment filenames (parts where `filename` is non-empty).

Q: How to handle the case where fewer than 3 matches exist?  
A: Print whatever matches were found (could be 0, 1, or 2). If zero, print a friendly "no matches
found" message and exit with code 0 (this is not an error). Only auth/network failures get non-zero
exit codes.

Q: How to handle a message with multiple attachments?  
A: List all attachment filenames for that email (e.g., comma-separated or one per line in the output
block).

Q: How to handle inline images / parts without filenames?  
A: Only count parts that have a non-empty `filename` field as attachments. Inline images without
filenames are ignored. (We rely on `has:attachment` for primary filtering; this client-side filename
collection is just for displaying filenames.)

Q: Python version?  
A: Python 3.9+ (modern baseline; uses standard typing if any).

Q: Module/file structure?  
A: Single file with a `main()` function and `if __name__ == '__main__': main()`. Helper functions
(e.g., `authenticate()`, `search_emails()`, `extract_attachment_filenames()`) inside the same file.

Q: Should `max_results` be configurable?  
A: No — hardcode to 3 as the task specifies. Pass `maxResults=3` to `users.messages.list` to avoid
fetching more than needed.

Q: What if the user's query already contains `has:attachment`?  
A: Just append `has:attachment` unconditionally; duplicate operators are harmless in Gmail search.

Q: Display date format?  
A: Use the raw Date header value as returned by Gmail (RFC 2822 format like "Mon, 1 Jan 2024
12:34:56 +0000"). No reformatting needed.

Q: What does the inline setup comment block need to cover?  
A: (1) Enable Gmail API in Google Cloud Console, (2) Create OAuth 2.0 Client ID (Desktop app), (3)
Download credentials.json and place it next to the script, (4)
`pip install google-auth-oauthlib google-api-python-client`, (5) First run opens browser for
consent; token.json is created automatically.

Q: How should the OAuth flow be triggered?  
A: Use `InstalledAppFlow.from_client_secrets_file(...).run_local_server(port=0)`. Refresh expired
tokens via `Credentials.from_authorized_user_file` + `creds.refresh(Request())` when possible; only
re-run the consent flow if refresh fails or no token exists.

Q: Should the script support multiple Gmail accounts?  
A: No — single account, single token.json.

Q: Should the script handle pagination?  
A: No — we only need 3 results; one page is enough. Use `maxResults=3`.

Q: Output style — exact formatting?  
A: One block per email, e.g.:

```
[1] Subject: <subject>
    From:    <sender>
    Date:    <date>
    Attachments: file1.pdf, file2.png
```

Blocks separated by blank lines. Exact whitespace is not critical as long as it's readable.

Q: Exit codes?  
A: 0 on success (including "no matches"), 1 for auth/credentials errors, 2 for API/network errors.
(Specific code values are not load-bearing; what matters is that non-zero is used for failures.)

Q: Should there be logging / verbose mode?  
A: No — keep it simple. Just print results and errors.

Q: Should we use type hints?  
A: Optional / light usage is fine. Not a requirement at complexity 3.

Q: Tests?  
A: Out of scope for this task. === PREPARED ANSWERS ===
