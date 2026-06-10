## Prompt

Write a detailed spec for the following request and save it as a markdown file: Create a simple
Python script that searches Gmail for emails matching a user-provided query, then returns the last 3
matching emails that have attachments.

## Other info

model: claude sonnet 4.6

# Evaluation Report

| Tier       | Criterion                                          | spec-1 | spec-2 | spec-3 |
| ---------- | -------------------------------------------------- | :----: | :----: | :----: |
| **MUST**   | OAuth 2.0 authentication with Gmail API            |  +10   |  -10   |  +10   |
| **MUST**   | CLI argument for search query                      |  +10   |  +10   |  +10   |
| **MUST**   | 3 most recent matching emails as the result        |  +10   |  +10   |  +10   |
| **MUST**   | Output per email: at least subject, sender, a…     |  +10   |  +10   |  +10   |
| **MUST**   | Required setup steps in Google Cloud Console:…     |  +10   |   0    |   +5   |
| **MUST**   | Graceful handling when there are no results        |  +10   |  +10   |  +10   |
| **SHOULD** | User having to download OAuth client secrets file  |   +3   |   0    |   +3   |
| **SHOULD** | Server-side result filtering                       |   0    |   +3   |   0    |
| **SHOULD** | Server-side result count limit                     |   +3   |   +3   |   +3   |
| **SHOULD** | Error handling for missing `credentials.json`      |   +3   |   0    |   +3   |
| **SHOULD** | API/network error handling                         |   +3   |   +3   |   +3   |
| **SHOULD** | Read-only OAuth scope                              |   +3   |   0    |   +3   |
| **SHOULD** | Caching OAuth tokens across runs                   |   +3   |   0    |   +3   |
| **SHOULD** | Browser-based OAuth consent flow on first run      |   +3   |   0    |   +3   |
| **COULD**  | Automatic token refresh on expiry                  |   +1   |   0    |   +1   |
| **COULD**  | Interactive query prompt as fallback when no…      |   0    |   0    |   0    |
| **COULD**  | Dependencies: gmail API libraries                  |   +1   |   0    |   +1   |
| **COULD**  | Dependency: `argparse` for CLI argument parsing    |   0    |   0    |   0    |
| **COULD**  | Excluding `credentials.json` and `token.json`…     |   +1   |   0    |   +1   |
| **COULD**  | Attachment downloading as explicitly out of scope  |   +1   |   +1   |   +1   |
| **COULD**  | Pagination as explicitly out of scope              |   +1   |   +1   |   +1   |
| **COULD**  | Multiple Gmail accounts as explicitly out of scope |   +1   |   0    |   +1   |

**Notes on non-obvious score assignments:**

**spec-1, Should #2 (Server-side result filtering) → 0:** The API call table shows `q=<query>` using
the raw user query with no `has:attachment` appended by the script. Attachment filtering is done
client-side by iterating candidate messages and inspecting MIME parts. The example invocation
`python gmail_attachments.py "has:attachment"` implies the user adds it manually.

**spec-2, Must #1 (OAuth 2.0 authentication) → -10:** Spec 2 explicitly lists "Authentication
handling (assumed to be pre-configured via MCP)" as a Non-Goal, directly contradicting this
criterion. The script delegates auth entirely to MCP infrastructure rather than implementing OAuth
2.0.

**spec-2, Must #5 (Google Cloud Console setup) → 0:** Because auth is a non-goal in this MCP-based
architecture, no setup steps are described and the criterion is simply absent.

**spec-2, Should #4,6,7,8 (credentials.json error, read-only scope, token.json caching, browser
flow) → 0:** All auth-related Should criteria are absent because authentication is wholly delegated
to MCP.

**spec-2, Should #5 (API/network error handling) → +3:** Addressed via MCP error handling ("MCP tool
call fails | Print error message with tool name and returned error, exit 2"). Different mechanism
than `HttpError` but the concept is fully covered since the parenthetical is clarifying rather than
a required checklist.

**spec-3, Must #5 (Google Cloud Console setup) → +5 (half credit):** Spec 3 shows awareness — it
labels `credentials.json` as "a Google Cloud OAuth client secrets file (download from GCP)" and
error handling "pointing the user to the Google Cloud Console" — but has no dedicated setup section
describing the steps to create a GCP project, enable the Gmail API, and create an OAuth Desktop App
credential.

**spec-3, Should #2 (Server-side result filtering) → 0:** The algorithm passes the user's raw query
to `users.messages.list` with no mention of appending `has:attachment`. A usage example even shows
the user manually adding `"has:attachment label:inbox"`, confirming client-side filtering.

| Tier                  | spec-1  | spec-2  | spec-3  |
| --------------------- | ------- | ------- | ------- |
| Must (out of 6)       | 6       | 4 / -1  | 6       |
| Should (out of 8)     | 7       | 3       | 7       |
| Could (out of 8)      | 6       | 2       | 6       |
| Total points (92 max) | 87      | 41      | 82      |
| **Score**             | **95%** | **45%** | **89%** |
