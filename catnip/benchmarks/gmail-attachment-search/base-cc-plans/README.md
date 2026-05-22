## Prompt

Write a plan for the following request and save it as a markdown file `plan.md`: Create a simple
Python script that searches Gmail for emails matching a user-provided query, then returns the last 3
matching emails that have attachments.

## Other info

model: claude sonnet 4.6

# Content evaluation report

| Tier       | Criterion                                          | plan-1 | plan-2 | plan-3 |
| ---------- | -------------------------------------------------- | ------ | ------ | ------ |
| **MUST**   | OAuth 2.0 authentication with Gmail API            | +10    | +10    | +10    |
| **MUST**   | CLI argument for search query                      | +10    | +10    | +10    |
| **MUST**   | 3 most recent matching emails as the result        | +10    | +10    | +10    |
| **MUST**   | Output per email: at least subject, sender, a…     | +10    | +10    | -10    |
| **MUST**   | Required setup steps in Google Cloud Console:…     | +10    | +10    | +5     |
| **MUST**   | Graceful handling when there are no results        | +10    | +10    | +10    |
| **SHOULD** | User having to download OAuth client secrets file  | +3     | +3     | +3     |
| **SHOULD** | Server-side result filtering                       | +3     | +3     | +3     |
| **SHOULD** | Server-side result count limit                     | +3     | +3     | +3     |
| **SHOULD** | Error handling for missing `credentials.json`      | +3     | +3     | +3     |
| **SHOULD** | API/network error handling                         | +3     | +3     | +3     |
| **SHOULD** | Read-only OAuth scope                              | +3     | +3     | +3     |
| **SHOULD** | Caching OAuth tokens across runs                   | +3     | +3     | +3     |
| **SHOULD** | Browser-based OAuth consent flow on first run      | +3     | +3     | +3     |
| **COULD**  | Automatic token refresh on expiry                  | +1     | +1     | +1     |
| **COULD**  | Interactive query prompt as fallback when no …     | +1     | +1     | 0      |
| **COULD**  | Dependencies: gmail API libraries                  | +1     | +1     | +1     |
| **COULD**  | Dependency: `argparse` for CLI argument parsing    | +1     | 0      | 0      |
| **COULD**  | Excluding `credentials.json` and `token.json`…     | 0      | 0      | +1     |
| **COULD**  | Attachment downloading as explicitly out of scope  | +1     | +1     | +1     |
| **COULD**  | Pagination as explicitly out of scope              | +1     | +1     | +1     |
| **COULD**  | Multiple Gmail accounts as explicitly out of scope | +1     | +1     | +1     |

**Notes on non-obvious score assignments:**

- **Output per email — plan-3: −10**: The output format explicitly shows Subject, From, Date, and
  Message ID with no attachment filenames. The implementation uses `format='metadata'` with only
  specific header fields, with no mechanism to extract attachment filenames. Scored as
  contradiction.
- **Required setup steps — plan-3: +5**: Prerequisites mention "A Google Cloud project with the
  Gmail API enabled" (enabling API ✓) and credentials downloaded — but the OAuth Desktop App
  credential type is not specified. Partial credit.
- **API/network error handling — plan-2: +3**: Says "let the exception propagate with its message;
  no silent swallowing" rather than catching `HttpError` explicitly. Credit given since the scenario
  is addressed and the error reaches the user.
- **Automatic token refresh — plan-1: +1**: Mentioned indirectly in the design decisions table
  ("handles token refresh") as a reason for the library choice, rather than as an explicit
  implementation step.

| Tier                  | plan-1  | plan-2  | plan-3  |
| --------------------- | ------- | ------- | ------- |
| Must (out of 6)       | 6       | 6       | 5 / -1  |
| Should (out of 8)     | 8       | 8       | 8       |
| Could (out of 8)      | 7       | 6       | 6       |
| Total points (92 max) | 91      | 90      | 65      |
| **Score**             | **99%** | **98%** | **71%** |

# Structure Evaluation Report

**File mapping:**
- `plan-1` → `base-cc-plans/plan-1.md`
- `plan-2` → `base-cc-plans/plan-2.md`
- `plan-3` → `base-cc-plans/plan-3.md`

## Topics comparison

| Topic | plan-1 | plan-2 | plan-3 |
|---|---|---|---|
| Goal | 3 | 3 | 3 |
| Requirements | 0 | 0 | 0 |
| Solution | 3 | 2 | 2 |
| Out of scope | 3 | 3 | 3 |
| Uncertainty | 2 | 2 | 2 |
| **Total (max 17)** | **11** | **10** | **10** |

**Notes on non-obvious scores:**

- **Requirements (0 for all):** None of the plans have verifiable acceptance/testing criteria. All three describe *what the script will do* (in Approach/Implementation sections), but never as a checklist of pass/fail criteria. There's no way to tell from the document alone whether a given implementation satisfies the spec.

- **Solution — plan-1 (3):** Gets +2 for the explicit `## Approach` section and +1 for the `## Key Design Decisions` table, which discusses rationale (e.g. server-side vs. client-side filtering, least-privilege scope). Plans 2 and 3 get +2 for a clear Approach section but no trade-off or alternative discussion.

- **Uncertainty (2 for all):** Each plan has a dedicated `## Error Handling` or `## Edge Cases` section covering risk scenarios (+1 for risks, +1 for dedicated section). None list assumptions or open questions.

## Metrics comparison

| Metric | plan-1 | plan-2 | plan-3 |
|---|---|---|---|
| Word count | 522 | 430 | 350 |
| Avg section length | 35.3 | 39.0 | 23.7 |
| Avg paragraph length | 20.0 | 22.7 | 19.3 |
| Avg bullet length | 8.1 | 7.9 | 7.2 |
| Code snippets ratio | 24% | 32% | 28% |

## Summary

All three plans share the same structural skeleton and nearly identical scores. The universal gap is **Requirements** — none establish verifiable acceptance criteria that would let someone test the spec independently of reading the implementation plan.
