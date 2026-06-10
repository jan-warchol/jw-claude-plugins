## Prompt

Write a plan for the following request and save it as a markdown file `plan.md`: Create a simple
Python script that searches Gmail for emails matching a user-provided query, then returns the last 3
matching emails that have attachments.

## Other info

model: claude sonnet 4.6

## Evaluation summaries

|                  | plan-1  | plan-2  | plan-3  | 152-w   | 199-w   | 274-w    | 468-w    | typical |
| ---------------- | ------- | ------- | ------- | ------- | ------- | -------- | -------- | ------- |
| Technical score  | **99%** | **98%** | **71%** | **88%** | **91%** | **100%** | **100%** | **98%** |
| Structural score | **11**  | **10**  | **10**  | **8**   | **5**   | **8**    | **9**    | **8**   |
| Word count       | 522     | 430     | 350     | 160     | 207     | 286      | 509      | 356     |

# Evaluations - "raw" plans

## Technical evaluation report

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

## Structural Evaluation Report

**File mapping:**

- `plan-1` → `base-cc-plans/plan-1.md`
- `plan-2` → `base-cc-plans/plan-2.md`
- `plan-3` → `base-cc-plans/plan-3.md`

### Topics comparison

| Topic              | plan-1 | plan-2 | plan-3 |
| ------------------ | ------ | ------ | ------ |
| Goal               | 3      | 3      | 3      |
| Requirements       | 0      | 0      | 0      |
| Solution           | 3      | 2      | 2      |
| Out of scope       | 3      | 3      | 3      |
| Uncertainty        | 2      | 2      | 2      |
| **Total (max 17)** | **11** | **10** | **10** |

**Notes on non-obvious scores:**

- **Requirements (0 for all):** None of the plans have verifiable acceptance/testing criteria. All
  three describe _what the script will do_ (in Approach/Implementation sections), but never as a
  checklist of pass/fail criteria. There's no way to tell from the document alone whether a given
  implementation satisfies the spec.

- **Solution — plan-1 (3):** Gets +2 for the explicit `## Approach` section and +1 for the
  `## Key Design Decisions` table, which discusses rationale (e.g. server-side vs. client-side
  filtering, least-privilege scope). Plans 2 and 3 get +2 for a clear Approach section but no
  trade-off or alternative discussion.

- **Uncertainty (2 for all):** Each plan has a dedicated `## Error Handling` or `## Edge Cases`
  section covering risk scenarios (+1 for risks, +1 for dedicated section). None list assumptions or
  open questions.

### Metrics comparison

| Metric               | plan-1 | plan-2 | plan-3 |
| -------------------- | ------ | ------ | ------ |
| Word count           | 522    | 430    | 350    |
| Avg section length   | 35.3   | 39.0   | 23.7   |
| Avg paragraph length | 20.0   | 22.7   | 19.3   |
| Avg bullet length    | 8.1    | 7.9    | 7.2    |
| Code snippets ratio  | 24%    | 32%    | 28%    |

### Summary

All three plans share the same structural skeleton and nearly identical scores. The universal gap is
**Requirements** — none establish verifiable acceptance criteria that would let someone test the
spec independently of reading the implementation plan.

# Evaluations - combined plans

**File mapping:**

- **152-w** = base-cc-plans/combined-plan-152-words.md
- **199-w** = base-cc-plans/combined-plan-199-words.md
- **274-w** = base-cc-plans/combined-plan-274-words.md
- **468-w** = base-cc-plans/combined-plan-468-words.md

## Structural Evaluation

### Topics comparison

| Topic              | 152-w | 199-w | 274-w | 468-w |
| ------------------ | ----- | ----- | ----- | ----- |
| Goal               | 3     | 3     | 3     | 3     |
| Requirements       | 0     | 0     | 0     | 0     |
| Solution           | 2     | 2     | 2     | 3     |
| Out of scope       | 3     | 0     | 3     | 3     |
| Uncertainty        | 0     | 0     | 0     | 0     |
| **Total (max 17)** | **8** | **5** | **8** | **9** |

**Notes:**

- **Goal (all = 3):** 152-w's "Overview" section opens with the goal in the first sentence, which
  qualifies per the "title as H1 + goal in first paragraph" rule. 199-w opens with `**Goal:**` as a
  bold label in the first paragraph — same rule applies. 274-w and 468-w each have a dedicated
  `## Goal` heading.
- **Requirements (all = 0):** None of the specs have acceptance or testing criteria. Error handling
  tables in some specs describe specific behaviors, but they are framed as implementation
  instructions for error cases only, with no verifiable success criteria for the happy path.
- **Solution (468-w = 3):** The `## Key Design Decisions` table in 468-w explicitly lists choices
  (auth library, scope, query strategy, result limit, output format) with stated rationale for each
  — this earns the trade-offs point. The other three describe the solution clearly (+2) but without
  any explicit reasoning about decisions or options.
- **Out of scope (199-w = 0):** 199-w is the only spec without an Out of Scope section or any
  mention of explicit exclusions.
- **Uncertainty (all = 0):** No spec mentions risks, assumptions, or open questions.

### Metrics comparison

| Metric               | 152-w | 199-w | 274-w | 468-w |
| -------------------- | ----- | ----- | ----- | ----- |
| Word count           | 160   | 207   | 286   | 509   |
| Avg section length   | 36.0  | 39.2  | 25.5  | 32.4  |
| Avg paragraph length | 36.0  | 23.1  | 23.3  | 25.1  |
| Avg bullet length    | 9.3   | 11.5  | 5.7   | 7.0   |
| Code char ratio      | 27%   | 34%   | 31%   | 31%   |

## Technical Evaluation

**Criteria file:** tech-criteria.md

### Criteria scores

| Tier       | Criterion                                     | 152-w | 199-w | 274-w | 468-w |
| ---------- | --------------------------------------------- | ----- | ----- | ----- | ----- |
| **MUST**   | OAuth 2.0 authentication with Gmail API       | +10   | +10   | +10   | +10   |
| **MUST**   | CLI argument for search query                 | +10   | +10   | +10   | +10   |
| **MUST**   | 3 most recent matching emails as the result   | +10   | +10   | +10   | +10   |
| **MUST**   | Output per email: at least subject, sender…   | +10   | +10   | +10   | +10   |
| **MUST**   | Required setup steps in Google Cloud Consol…  | +10   | +5    | +10   | +10   |
| **MUST**   | Graceful handling when there are no results   | 0     | +10   | +10   | +10   |
| **SHOULD** | User having to download OAuth client secrets… | +3    | +3    | +3    | +3    |
| **SHOULD** | Server-side result filtering                  | +3    | +3    | +3    | +3    |
| **SHOULD** | Server-side result count limit                | +3    | +3    | +3    | +3    |
| **SHOULD** | Error handling for missing `credentials.json` | +3    | +3    | +3    | +3    |
| **SHOULD** | API/network error handling                    | +3    | +3    | +3    | +3    |
| **SHOULD** | Read-only OAuth scope                         | +3    | +3    | +3    | +3    |
| **SHOULD** | Caching OAuth tokens across runs              | +3    | +3    | +3    | +3    |
| **SHOULD** | Browser-based OAuth consent flow on first ru… | +3    | +3    | +3    | +3    |
| **COULD**  | Automatic token refresh on expiry             | 0     | +1    | +1    | +1    |
| **COULD**  | Interactive query prompt as fallback when no… | +1    | +1    | +1    | +1    |
| **COULD**  | Dependencies: gmail API libraries             | +1    | +1    | +1    | +1    |
| **COULD**  | Dependency: `argparse` for CLI argument pars… | +1    | +1    | +1    | +1    |
| **COULD**  | Excluding `credentials.json` and `token.jso…` | +1    | +1    | +1    | +1    |
| **COULD**  | Attachment downloading as explicitly out of…  | +1    | 0     | +1    | +1    |
| **COULD**  | Pagination as explicitly out of scope         | +1    | 0     | +1    | +1    |
| **COULD**  | Multiple Gmail accounts as explicitly out o…  | +1    | 0     | +1    | +1    |

**Notes:**

- **199-w, "Required setup steps" (+5):** Presents both requirements (Gmail API enabled, OAuth 2.0
  Desktop App credentials) as prerequisites — acknowledges they are needed but does not describe the
  steps to create them in Google Cloud Console. Half credit per the "mentions a file exists but not
  that it must be created/obtained" rule.
- **152-w, "Automatic token refresh" (0):** Mentions only the failure case ("Token refresh failure:
  delete `token.json`…") without stating that automatic/silent refresh is attempted on expiry.
  199-w, 274-w, and 468-w all use the phrase "silent refresh failure," which implies the mechanism
  is attempted.
- **199-w, out-of-scope items (all 0):** Has no Out of Scope section and makes no mention of
  attachment downloading, pagination, or multiple accounts being excluded.

### Summary

| Tier                  | 152-w   | 199-w   | 274-w    | 468-w    |
| --------------------- | ------- | ------- | -------- | -------- |
| Must (out of 6)       | 5+ 1-   | 5+ 1±   | 6+       | 6+       |
| Should (out of 8)     | 8+      | 8+      | 8+       | 8+       |
| Could (out of 8)      | 7+      | 5+      | 8+       | 8+       |
| Total points (92 max) | 81      | 84      | 92       | 92       |
| **Score**             | **88%** | **91%** | **100%** | **100%** |
