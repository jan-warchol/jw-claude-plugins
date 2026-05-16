## Prompt

Write a plan for the following request and save it as a markdown file `plan.md`: Create a simple Python script that searches Gmail for emails matching a user-provided query, then returns the last 3 matching emails that have attachments.

## Other info

model: claude sonnet 4.6

# Evaluation report

| Tier | Criterion | plan-1 | plan-2 | plan-3 |
|------|-----------|--------|--------|--------|
| **MUST** | OAuth 2.0 authentication with Gmail API | +10 | +10 | +10 |
| **MUST** | CLI argument for search query | +10 | +10 | +10 |
| **MUST** | 3 most recent matching emails as the result | +10 | +10 | +10 |
| **MUST** | Output per email: at least subject, sender, a… | +10 | +10 | -10 |
| **MUST** | Required setup steps in Google Cloud Console:… | +10 | +10 | +5 |
| **MUST** | Graceful handling when there are no results | +10 | +10 | +10 |
| **SHOULD** | User having to download OAuth client secrets file | +3 | +3 | +3 |
| **SHOULD** | Server-side result filtering | +3 | +3 | +3 |
| **SHOULD** | Server-side result count limit | +3 | +3 | +3 |
| **SHOULD** | Error handling for missing `credentials.json` | +3 | +3 | +3 |
| **SHOULD** | API/network error handling | +3 | +3 | +3 |
| **SHOULD** | Read-only OAuth scope | +3 | +3 | +3 |
| **SHOULD** | Caching OAuth tokens across runs | +3 | +3 | +3 |
| **SHOULD** | Browser-based OAuth consent flow on first run | +3 | +3 | +3 |
| **COULD** | Automatic token refresh on expiry | +1 | +1 | +1 |
| **COULD** | Interactive query prompt as fallback when no … | +1 | +1 | 0 |
| **COULD** | Dependencies: gmail API libraries | +1 | +1 | +1 |
| **COULD** | Dependency: `argparse` for CLI argument parsing | +1 | 0 | 0 |
| **COULD** | Excluding `credentials.json` and `token.json`… | 0 | 0 | +1 |
| **COULD** | Attachment downloading as explicitly out of scope | +1 | +1 | +1 |
| **COULD** | Pagination as explicitly out of scope | +1 | +1 | +1 |
| **COULD** | Multiple Gmail accounts as explicitly out of scope | +1 | +1 | +1 |

**Notes on non-obvious score assignments:**

- **Output per email — plan-3: −10**: The output format explicitly shows Subject, From, Date, and Message ID with no attachment filenames. The implementation uses `format='metadata'` with only specific header fields, with no mechanism to extract attachment filenames. Scored as contradiction.
- **Required setup steps — plan-3: +5**: Prerequisites mention "A Google Cloud project with the Gmail API enabled" (enabling API ✓) and credentials downloaded — but the OAuth Desktop App credential type is not specified. Partial credit.
- **API/network error handling — plan-2: +3**: Says "let the exception propagate with its message; no silent swallowing" rather than catching `HttpError` explicitly. Credit given since the scenario is addressed and the error reaches the user.
- **Automatic token refresh — plan-1: +1**: Mentioned indirectly in the design decisions table ("handles token refresh") as a reason for the library choice, rather than as an explicit implementation step.

| Tier | plan-1 | plan-2 | plan-3 |
|---|--------|--------|--------|
| Must (out of 6) | 6 | 6 | 5 / -1 |
| Should (out of 8) | 8 | 8 | 8 |
| Could (out of 8) | 7 | 6 | 6 |
| Total points (92 max) | 91 | 90 | 65 |
| **Score** | **99%** | **98%** | **71%** |
