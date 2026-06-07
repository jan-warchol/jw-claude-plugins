# Gmail Attachment Search Script

## Purpose

CLI Python script that queries a user's Gmail account with a search string and prints metadata for
the 3 most recent matching emails that contain attachments.

## Requirements

- Accepts a Gmail search query as a CLI argument
- Authenticates via OAuth2 using `google-api-python-client`
- Outputs for each of the 3 results: subject, sender, date, attachment filenames
- Emails without attachments are excluded from results
- Does not download attachments or modify messages

## Solution

- Use `users.messages.list` with the `q` parameter to apply the user's query
- Load OAuth2 credentials from `credentials.json`; cache tokens in `token.json`
- Fetch messages in pages; for each, call `users.messages.get` (format `full`) and inspect MIME
  parts for non-inline attachments
- Stop once 3 qualifying emails are found

## Uncertainty

- OAuth2 requires a Google Cloud Console project with Gmail API enabled; `credentials.json` must
  be provided by the user
- Heavily filtered queries or sparse attachment use may require many pagination rounds
