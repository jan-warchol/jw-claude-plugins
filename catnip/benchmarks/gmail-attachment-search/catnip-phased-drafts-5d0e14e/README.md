# Process

Run below prompts, each in a **new** Claude Code session:

```
/catnip:draft-spec Create a simple Python script that searches Gmail for emails matching a user-provided query, then returns the last 3 matching emails that have attachments.
/catnip:enrich-spec initial.md
/catnip:compress-spec enriched.md
```

- model: sonnet 4.6
- effort: high (?)

Note: quite frequently the agent drops "assumptions" section, stating that it is obvious.

As for the `compressed.md`, I'm not sure how I obtained it... I think it was during fine-tuning
of the compression skill.

# Evaluations

**File mapping:**

- **comp-1** = catnip-phased-drafts-5d0e14e/compressed-1.md
- **comp-2** = catnip-phased-drafts-5d0e14e/compressed-2.md
- **comp-3** = catnip-phased-drafts-5d0e14e/compressed-3.md
- **comp-4** = catnip-phased-drafts-5d0e14e/compressed-4.md
- **comp-5** = catnip-phased-drafts-5d0e14e/compressed-5.md
- **comp** = catnip-phased-drafts-5d0e14e/compressed.md

---

## Structural Evaluation

### Topics comparison

| Topic              | comp-1 | comp-2 | comp-3 | comp-4 | comp-5 | comp   |
| ------------------ | ------ | ------ | ------ | ------ | ------ | ------ |
| Goal               | 3      | 3      | 3      | 3      | 3      | 3      |
| Requirements       | 2      | 3      | 3      | 3      | 3      | 2      |
| Solution           | 1      | 1      | 2      | 4      | 1      | 3      |
| Out of scope       | 3      | 3      | 3      | 3      | 3      | 3      |
| Uncertainty        | 0      | 3      | 2      | 0      | 0      | 3      |
| **Total (max 17)** | **9**  | **13** | **13** | **13** | **10** | **14** |

**Notes:**

- **Requirements, comp-1 and comp (2):** Verifiable criteria are scattered across
  `## Outputs`/`## Behavior`/`## Error Handling` with no dedicated requirements section. The other
  four each have a dedicated `## Functional Requirements` section.
- **Solution, comp-4 (4):** The only spec to earn all four solution points. `## Design Notes` names
  an explicit alternative ("OAuth 2.0 preferred over service accounts") and discusses a trade-off
  ("Fixed count of 3 keeps output minimal; `--count` flag deferred" — configurability sacrificed for
  simplicity).
- **Solution, comp-3 (2):** `## Implementation Notes` clearly articulates specific technical choices
  — fetching 10 candidates via `messages.list`, using `format=metadata` to avoid body transfer, and
  a local MIME check alongside the API filter — each with stated reasoning.
- **Solution, comp (3):** `## Design Choices` names IMAP as a rejected alternative with rationale,
  earning the alternatives point. No trade-off discussion.
- **Uncertainty, comp-2 (3):** `## Assumptions and Risks` lists two items: a prerequisite assumption
  (GCP project + OAuth credentials) and a security risk ("`token.json` is plaintext; protect from
  unauthorized access and version control").
- **Uncertainty, comp-3 (2):** `## Assumptions` lists two assumptions (credentials.json required; no
  fallback pagination if first 10 results don't include 3 with attachments). No risks section.
- **Uncertainty, comp (3):** `## Assumptions and Risks` covers a prerequisite assumption (GCP
  project + credentials.json), a headless environment risk (browser required for initial OAuth), and
  a quota risk (no retry logic).

### Metrics comparison

| Metric               | comp-1 | comp-2 | comp-3 | comp-4 | comp-5 | comp |
| -------------------- | ------ | ------ | ------ | ------ | ------ | ---- |
| Word count           | 235    | 202    | 241    | 186    | 211    | 224  |
| Avg section length   | 23.9   | 22.9   | 32.1   | 28.3   | 39.4   | 19.8 |
| Avg paragraph length | 22.2   | 20.3   | 27.6   | 15.5   | 18.7   | 16.9 |
| Avg bullet length    | 8.8    | 8.3    | 13.9   | 8.6    | 9.7    | 8.1  |
| Code char ratio      | 28%    | 14%    | 28%    | 12%    | 28%    | 23%  |

---

## Technical Evaluation

**Criteria file:** tech-criteria.md

### Criteria scores

| Tier       | Criterion                                     | comp-1 | comp-2 | comp-3 | comp-4 | comp-5 | comp |
| ---------- | --------------------------------------------- | ------ | ------ | ------ | ------ | ------ | ---- |
| **MUST**   | OAuth 2.0 authentication with Gmail API       | +10    | +10    | +10    | +10    | +10    | +10  |
| **MUST**   | CLI argument for search query                 | +10    | +10    | +10    | +10    | +10    | +10  |
| **MUST**   | 3 most recent matching emails as the result   | +10    | +10    | +10    | +10    | +10    | +10  |
| **MUST**   | Output per email: at least subject, sender…   | +10    | +10    | +10    | +10    | +10    | +10  |
| **MUST**   | Required setup steps in Google Cloud Consol…  | 0      | +5     | +5     | 0      | +5     | +5   |
| **MUST**   | Graceful handling when there are no results   | +10    | +10    | +10    | +10    | +10    | +10  |
| **SHOULD** | User having to download OAuth client secrets… | +3     | +3     | +3     | +2     | +3     | +3   |
| **SHOULD** | Server-side result filtering                  | +3     | +3     | +3     | +3     | +3     | +3   |
| **SHOULD** | Server-side result count limit                | +2     | +2     | −3     | +2     | +2     | +3   |
| **SHOULD** | Error handling for missing `credentials.json` | +3     | +3     | +3     | +2     | +3     | +3   |
| **SHOULD** | API/network error handling                    | +3     | +3     | +3     | +3     | +3     | +3   |
| **SHOULD** | Read-only OAuth scope                         | +3     | +3     | +3     | +3     | +3     | +3   |
| **SHOULD** | Caching OAuth tokens across runs              | +3     | +3     | +3     | +3     | +3     | +3   |
| **SHOULD** | Browser-based OAuth consent flow on first ru… | +3     | +3     | +3     | +3     | 0      | +3   |
| **COULD**  | Automatic token refresh on expiry             | +1     | 0      | 0      | 0      | +1     | 0    |
| **COULD**  | Interactive query prompt as fallback when no… | 0      | 0      | 0      | 0      | 0      | 0    |
| **COULD**  | Dependencies: gmail API libraries             | +1     | +1     | +1     | +1     | +1     | +1   |
| **COULD**  | Dependency: `argparse` for CLI argument pars… | 0      | 0      | 0      | 0      | 0      | 0    |
| **COULD**  | Excluding `credentials.json` and `token.jso…` | +1     | +1     | 0      | 0      | 0      | 0    |
| **COULD**  | Attachment downloading as explicitly out of…  | +1     | +1     | +1     | +1     | +1     | +1   |
| **COULD**  | Pagination as explicitly out of scope         | +1     | +1     | +1     | +1     | +1     | +1   |
| **COULD**  | Multiple Gmail accounts as explicitly out o…  | +1     | 0      | +1     | +1     | 0      | 0    |

**Notes:**

- **comp-1 and comp-4, Google Cloud setup (0):** Neither mentions Google Cloud Console. comp-1's
  error handling says "actionable error explaining how to obtain it" without naming GCC; comp-4 says
  credentials.json is "read from working directory or `$GMAIL_CREDENTIALS`" with no sourcing
  information.
- **comp-3, server-side result count limit (−3):** Implementation Notes explicitly describes
  fetching 10 candidate IDs via `messages.list` then locally checking for 3 with attachments —
  client-side truncation from a pool of 10, contradicting the criterion.
- **comp, server-side result count limit (+3):** "Request first 3 results from the API (newest-first
  by default)" is the clearest statement among all evaluated specs that the count limit is applied
  at the API level.
- **comp-4, user having to download credentials (+2):** credentials.json described as required in
  working directory but no mention of where to obtain it.
- **comp-4, error handling for missing credentials (+2):** "On auth/API error: print descriptive
  message to stderr, exit non-zero" is generic — missing credentials.json is not called out
  specifically and no setup instructions are mentioned.
- **comp-5, browser OAuth flow (0):** Authentication describes caching and auto-refresh but never
  mentions a browser opening on first run.
- **comp-1, gitignore (+1):** `token.json is gitignored` in Authentication, plus both files marked
  "(gitignored)" in the Files section.
- **comp-2, gitignore (+1):** "token.json is plaintext; protect from unauthorized access and version
  control" addresses version control exclusion.

### Summary

| Tier                  | comp-1  | comp-2  | comp-3  | comp-4  | comp-5  | comp    |
| --------------------- | ------- | ------- | ------- | ------- | ------- | ------- |
| Must (out of 6)       | 5+      | 5+ 1±   | 5+ 1±   | 5+      | 5+ 1±   | 5+ 1±   |
| Should (out of 8)     | 7+ 1±   | 7+ 1±   | 7+ 1-   | 5+ 3±   | 7+ 1±   | 8+      |
| Could (out of 8)      | 6+      | 4+      | 4+      | 4+      | 4+      | 3+      |
| Total points (92 max) | 79      | 82      | 77      | 75      | 79      | 82      |
| **Score**             | **86%** | **89%** | **84%** | **82%** | **86%** | **89%** |
