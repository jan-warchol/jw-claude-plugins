## Prompt

Write a plan for the following request and save it as a markdown file `plan.md`: Create a simple
Python script that searches Gmail for emails matching a user-provided query, then returns the last 3
matching emails that have attachments. Before starting the implementation, write a plan and save it
as a markdown file.

## Other info

model: claude sonnet 4.6

# Evaluation Report

| Tier       | Criterion                                          | plan-1 | plan-2 | plan-3 | typical | combined |
| ---------- | -------------------------------------------------- | ------ | ------ | ------ | ------- | -------- |
| **MUST**   | OAuth 2.0 authentication with Gmail API            | +10    | +10    | +10    | +10     | +10      |
| **MUST**   | CLI argument for search query                      | +10    | +10    | +10    | +10     | +10      |
| **MUST**   | 3 most recent matching emails as the result        | +10    | +10    | +10    | +10     | +10      |
| **MUST**   | Output per email: at least subject, sender, a…     | +10    | +10    | +10    | +10     | +10      |
| **MUST**   | Required setup steps in Google Cloud Console       | +5     | +5     | +5     | +5      | +5       |
| **MUST**   | Graceful handling when there are no results        | +10    | +10    | +10    | +10     | +10      |
| **SHOULD** | User having to download OAuth client secrets file  | +3     | +3     | +3     | +3      | +3       |
| **SHOULD** | Server-side result filtering                       | +3     | +3     | +3     | +3      | +3       |
| **SHOULD** | Server-side result count limit                     | +3     | +3     | +3     | +3      | +3       |
| **SHOULD** | Error handling for missing `credentials.json`      | +3     | +3     | +3     | +3      | +3       |
| **SHOULD** | API/network error handling                         | 0      | 0      | 0      | 0       | 0        |
| **SHOULD** | Read-only OAuth scope                              | +3     | +3     | +3     | +3      | +3       |
| **SHOULD** | Caching OAuth tokens across runs                   | +3     | +3     | +3     | +3      | +3       |
| **SHOULD** | Browser-based OAuth consent flow on first run      | +3     | 0      | 0      | +3      | +3       |
| **COULD**  | Automatic token refresh on expiry                  | +1     | 0      | 0      | +1      | +1       |
| **COULD**  | Interactive query prompt as fallback when no…      | 0      | +1     | +1     | +1      | +1       |
| **COULD**  | Dependencies: gmail API libraries                  | +1     | +1     | +1     | +1      | +1       |
| **COULD**  | Dependency: `argparse` for CLI argument parsing    | 0      | 0      | 0      | 0       | 0        |
| **COULD**  | Excluding `credentials.json` and `token.json`…     | 0      | 0      | 0      | 0       | 0        |
| **COULD**  | Attachment downloading as explicitly out of scope  | 0      | 0      | 0      | 0       | 0        |
| **COULD**  | Pagination as explicitly out of scope              | 0      | 0      | 0      | 0       | 0        |
| **COULD**  | Multiple Gmail accounts as explicitly out of scope | 0      | 0      | 0      | 0       | 0        |

**Notes on non-obvious score assignments:**

- **Required setup steps in Google Cloud Console (all plans, +5):** All plans mention
  `credentials.json` downloaded from Google Cloud Console, showing awareness that GCC is involved.
  None explicitly describes the setup steps (enabling the Gmail API, creating an OAuth Desktop App
  credential). Half credit given to all.
- **Browser-based OAuth consent flow (plan-2, plan-3: 0):** plan-2 says only "Authenticate with
  OAuth2 using a `credentials.json` file and cache the token in `token.json`" — no mention of what
  happens on first run. plan-3 similarly omits the browser consent step.
- **Excluding credentials.json and token.json from VCS (all plans, 0):** Several plans mark
  `credentials.json` as "not committed" in their file layout, but none marks `token.json` the same
  way. Could criteria have no partial credit, so all score 0.
- **Server-side result count limit (plan-3, +3):** plan-3 says "requesting up to 3 results" via the
  API call without naming `maxResults` explicitly — the concept is substantively addressed.

| Tier                  | plan-1  | plan-2  | plan-3  | typical | combined |
| --------------------- | ------- | ------- | ------- | ------- | -------- |
| Must (out of 6)       | 6       | 6       | 6       | 6       | 6        |
| Should (out of 8)     | 7       | 6       | 6       | 7       | 7        |
| Could (out of 8)      | 2       | 2       | 2       | 3       | 3        |
| Total points (92 max) | 78      | 75      | 75      | 79      | 79       |
| **Score**             | **85%** | **82%** | **82%** | **86%** | **86%**  |

# Structural Evaluation

**File mapping:**

- **plan-1** = cc-plans-alt/plan-1.md
- **plan-2** = cc-plans-alt/plan-2.md
- **plan-3** = cc-plans-alt/plan-3.md

## Topics comparison

| Topic              | plan-1 | plan-2 | plan-3 |
| ------------------ | ------ | ------ | ------ |
| Goal               | 3      | 3      | 3      |
| Requirements       | 0      | 0      | 0      |
| Solution           | 2      | 3      | 2      |
| Out of scope       | 0      | 0      | 0      |
| Uncertainty        | 0      | 0      | 0      |
| **Total (max 17)** | **5**  | **6**  | **5**  |

**Notes:**

- **Solution, plan-2 (3):** The `## Key Design Decisions` section names four explicit choices with
  rationale — `has:attachment` server-side filtering over local filtering, `format=metadata` for
  smaller responses, newest-first API default, minimal dependencies. The rationale contains
  trade-off reasoning ("more efficient than fetching arbitrary pages and filtering locally", "we
  don't need the full message body"), earning the trade-offs point. Plans 1 and 3 have an Approach
  section but no design decisions or trade-offs.
- **Out of scope (all = 0):** None of the three plans mentions any exclusions. This is the sharpest
  contrast with the combined plans, which all include an Out of Scope section except 199-w.

## Metrics comparison

| Metric               | plan-1 | plan-2 | plan-3 |
| -------------------- | ------ | ------ | ------ |
| Word count           | 216    | 322    | 222    |
| Avg section length   | 21.1   | 49.2   | 22.0   |
| Avg paragraph length | 19.9   | 46.2   | 20.3   |
| Avg bullet length    | 6.2    | 12.9   | 7.6    |
| Code char ratio      | 28%    | 24%    | 26%    |
