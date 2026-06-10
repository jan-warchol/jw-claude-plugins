## Prompt

Write a detailed plan for the following request and save it as a markdown file: Create a simple
Python script that searches Gmail for emails matching a user-provided query, then returns the last 3
matching emails that have attachments.

## Other info

model: claude sonnet 4.6

# Evaluation report

| Tier       | Criterion                                          | plan-1 | plan-2 | plan-3 |
| ---------- | -------------------------------------------------- | ------ | ------ | ------ |
| **MUST**   | OAuth 2.0 authentication with Gmail API            | +10    | +10    | +10    |
| **MUST**   | CLI argument for search query                      | +10    | +10    | +10    |
| **MUST**   | 3 most recent matching emails as the result        | +10    | +10    | +10    |
| **MUST**   | Output per email: at least subject, sender, a…     | +10    | +10    | +10    |
| **MUST**   | Required setup steps in Google Cloud Console:…     | +10    | +10    | +10    |
| **MUST**   | Graceful handling when there are no results        | +10    | +10    | +10    |
| **SHOULD** | User having to download OAuth client secrets…      | +3     | +3     | +3     |
| **SHOULD** | Server-side result filtering                       | +3     | 0      | -3     |
| **SHOULD** | Server-side result count limit                     | +3     | +3     | +3     |
| **SHOULD** | Error handling for missing `credentials.json`      | +3     | +3     | +3     |
| **SHOULD** | API/network error handling                         | +1     | +2     | +2     |
| **SHOULD** | Read-only OAuth scope                              | +3     | +3     | +3     |
| **SHOULD** | Caching OAuth tokens across runs                   | +3     | +3     | +3     |
| **SHOULD** | Browser-based OAuth consent flow on first run      | +3     | +3     | +3     |
| **COULD**  | Automatic token refresh on expiry                  | +1     | +1     | +1     |
| **COULD**  | Interactive query prompt as fallback when no…      | +1     | +1     | 0      |
| **COULD**  | Dependencies: gmail API libraries (`google-api…    | +1     | +1     | +1     |
| **COULD**  | Dependency: `argparse` for CLI argument parsing    | 0      | 0      | +1     |
| **COULD**  | Excluding `credentials.json` and `token.json`…     | +1     | +1     | +1     |
| **COULD**  | Attachment downloading as explicitly out of scope  | +1     | +1     | +1     |
| **COULD**  | Pagination as explicitly out of scope              | 0      | 0      | +1     |
| **COULD**  | Multiple Gmail accounts as explicitly out of scope | +1     | +1     | 0      |

**Notes on non-obvious scores:**

- **Server-side result filtering**: plan-1 explicitly appends `has:attachment` server-side
  (`full_query = f"{query} has:attachment"`), earning full points. plan-2 passes the user query
  directly and filters client-side via `has_attachment()`, but never explicitly states opposition to
  the server-side approach — scored 0. plan-3 explicitly rejects server-side filtering: _"The query
  does **not** need to include `has:attachment`; we filter for attachments ourselves"_ — a direct
  contradiction, scoring -3.

- **API/network error handling**: Partial scores across all plans. plan-1 says _"let the exception
  surface with its message; no silent swallowing"_ — shows awareness that errors should be visible
  but does not catch them, so output would be a Python traceback rather than a user-friendly message
  (+1). plan-2 explicitly catches `HttpError 429` only; plan-3 explicitly handles HTTP 429 (with
  retry backoff) and HTTP 401 (re-auth) — both cover specific HttpError cases but not the general
  API error scenario (+2 each).

| Tier                  | plan-1  | plan-2  | plan-3  |
| --------------------- | ------- | ------- | ------- |
| Must (out of 6)       | 6       | 6       | 6       |
| Should (out of 8)     | 8       | 7       | 7 / -1  |
| Could (out of 8)      | 6       | 6       | 6       |
| Total points (92 max) | 88      | 86      | 83      |
| **Score**             | **96%** | **93%** | **90%** |
