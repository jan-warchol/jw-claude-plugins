## Prompt

Write a spec for the following request and save it as a markdown file `spec.md`: Create a simple
Python script that searches Gmail for emails matching a user-provided query, then returns the last 3
matching emails that have attachments.

## Other info

model: claude sonnet 4.6

# Evaluation Report

| Tier       | Criterion                                          | spec-1 | spec-2 | spec-3 |
| ---------- | -------------------------------------------------- | ------ | ------ | ------ |
| **MUST**   | OAuth 2.0 authentication with Gmail API            | +10    | +10    | +10    |
| **MUST**   | CLI argument for search query                      | +10    | +10    | +10    |
| **MUST**   | 3 most recent matching emails as the result        | +10    | +10    | +10    |
| **MUST**   | Output per email: at least subject, sender, a…     | +10    | +10    | +10    |
| **MUST**   | Required setup steps in Google Cloud Console:…     | 0      | +5     | 0      |
| **MUST**   | Graceful handling when there are no results        | +10    | +10    | +10    |
| **SHOULD** | User having to download OAuth client secrets file  | +1     | +3     | +1     |
| **SHOULD** | Server-side result filtering                       | +3     | +3     | +3     |
| **SHOULD** | Server-side result count limit                     | 0      | 0      | 0      |
| **SHOULD** | Error handling for missing `credentials.json`      | +3     | +3     | +3     |
| **SHOULD** | API/network error handling                         | +3     | +3     | +3     |
| **SHOULD** | Read-only OAuth scope                              | +3     | +3     | +3     |
| **SHOULD** | Caching OAuth tokens across runs                   | +3     | +3     | +3     |
| **SHOULD** | Browser-based OAuth consent flow on first run      | +3     | +3     | +3     |
| **COULD**  | Automatic token refresh on expiry                  | 0      | 0      | 0      |
| **COULD**  | Interactive query prompt as fallback when no …     | 0      | 0      | +1     |
| **COULD**  | Dependencies: gmail API libraries                  | +1     | +1     | +1     |
| **COULD**  | Dependency: `argparse` for CLI argument parsing    | 0      | 0      | 0      |
| **COULD**  | Excluding `credentials.json` and `token.json`…     | 0      | 0      | 0      |
| **COULD**  | Attachment downloading as explicitly out of scope  | +1     | +1     | +1     |
| **COULD**  | Pagination as explicitly out of scope              | +1     | +1     | +1     |
| **COULD**  | Multiple Gmail accounts as explicitly out of scope | +1     | +1     | +1     |

**Notes on non-obvious score assignments:**

- **Required setup steps in Google Cloud Console — spec-2 +5**: Mentions `credentials.json` is
  "downloaded from Google Cloud Console" — the download step is present, but enabling the API and
  creating Desktop App credentials are not described. Partial credit.
- **Required setup steps — spec-1 and spec-3: 0**: Spec-1 doesn't mention Google Cloud Console at
  all. Spec-3 says "standard Google Cloud OAuth 2.0 client secret file" — an incidental descriptor
  of the file type, not a description of required setup steps.
- **User having to download credentials.json — spec-1 and spec-3: +1**: Both describe
  `credentials.json` as the OAuth secrets file to have, but the download action is absent. Partial
  rounded down to 1 since only the file's identity, not its acquisition, is addressed.
- **Browser-based OAuth consent flow — spec-3: +3**: Says "prompt the user to authorize on first
  run" without the word "browser." Credit given as this describes the first-run authorization flow.

| Tier                  | spec-1  | spec-2  | spec-3  |
| --------------------- | ------- | ------- | ------- |
| Must (out of 6)       | 5       | 6       | 5       |
| Should (out of 8)     | 7       | 7       | 7       |
| Could (out of 8)      | 4       | 4       | 5       |
| Total points (92 max) | 73      | 80      | 74      |
| **Score**             | **79%** | **87%** | **80%** |
