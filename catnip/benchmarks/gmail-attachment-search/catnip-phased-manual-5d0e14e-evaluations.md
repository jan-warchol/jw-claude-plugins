# Evaluations — Gmail Attachment Search catnip-phased-manual-5d0e14e

**File mapping:**
- **comp-1** = catnip-phased-manual-5d0e14e/compressed-1.md
- **comp-2** = catnip-phased-manual-5d0e14e/compressed-2.md
- **comp-3** = catnip-phased-manual-5d0e14e/compressed-3.md
- **comp-4** = catnip-phased-manual-5d0e14e/compressed-4.md
- **comp-5** = catnip-phased-manual-5d0e14e/compressed-5.md

---

## Structural Evaluation

### Topics comparison

| Topic | comp-1 | comp-2 | comp-3 | comp-4 | comp-5 |
|---|---|---|---|---|---|
| Goal | 3 | 3 | 3 | 3 | 3 |
| Requirements | 2 | 3 | 3 | 2 | 3 |
| Solution | 3 | 3 | 3 | 1 | 3 |
| Out of scope | 3 | 3 | 3 | 3 | 3 |
| Uncertainty | 3 | 0 | 0 | 0 | 2 |
| **Total (max 17)** | **14** | **12** | **12** | **9** | **14** |

**Notes:**

- **Requirements:** comp-1 and comp-4 lack a dedicated requirements section — verifiable criteria are scattered across `## Behavior`, `## Output`, and `## Error handling`. comp-2, comp-3, and comp-5 each have a dedicated `## Functional Requirements` section.
- **Solution:** comp-1, comp-2, comp-3, comp-5 all have dedicated design decisions sections and explicitly name at least one alternative with reasoning for rejection. comp-4 has no design decisions section — the approach is described only implicitly across `## Behavior` and `## Authentication`. None of the five earn the trade-offs point; rationale explains benefits rather than explicit sacrifices.
- **Uncertainty, comp-1 (3):** `## Assumptions and Risks` covers both a prerequisite assumption (Google Cloud project + credentials.json) and two risks (quota errors causing exit, OAuth browser flow failing in headless environments).
- **Uncertainty, comp-5 (2):** `## Assumptions` explicitly lists two assumptions (+1 assumptions, +1 dedicated section). "Inline images not treated as attachments (revisit if needed)" is framed as an assumption note rather than an explicit open question. No risks mentioned.
- **Uncertainty, comp-2/3/4 (0):** No uncertainty content of any kind.

### Metrics comparison

| Metric | comp-1 | comp-2 | comp-3 | comp-4 | comp-5 |
|---|---|---|---|---|---|
| Word count | 258 | 217 | 195 | 191 | 231 |
| Avg section length | 26.1 | 24.9 | 30.0 | 21.8 | 23.7 |
| Avg paragraph length | 23.5 | 20.7 | 30.0 | 17.4 | 20.2 |
| Avg bullet length | 9.5 | 8.9 | 10.5 | 6.0 | 11.8 |
| Code char ratio | 14% | 21% | 14% | 17% | 19% |

---

## Technical Evaluation

**Criteria file:** tech-criteria.md

### Criteria scores

| Tier | Criterion | comp-1 | comp-2 | comp-3 | comp-4 | comp-5 |
|---|---|---|---|---|---|---|
| **MUST** | OAuth 2.0 authentication with Gmail API | +10 | +10 | +10 | +10 | +10 |
| **MUST** | CLI argument for search query | +10 | +10 | +10 | +10 | +10 |
| **MUST** | 3 most recent matching emails as the result | +10 | +10 | +10 | +10 | +10 |
| **MUST** | Output per email: at least subject, sender… | +10 | +10 | +10 | +10 | +10 |
| **MUST** | Required setup steps in Google Cloud Consol… | +5 | +5 | +5 | +5 | +5 |
| **MUST** | Graceful handling when there are no results | +10 | +10 | +10 | +10 | +10 |
| **SHOULD** | User having to download OAuth client secrets… | +3 | +3 | +3 | +3 | +3 |
| **SHOULD** | Server-side result filtering | +3 | +3 | +3 | +3 | +3 |
| **SHOULD** | Server-side result count limit | +2 | −3 | +2 | +2 | +2 |
| **SHOULD** | Error handling for missing `credentials.json` | +3 | +3 | +1 | +3 | +3 |
| **SHOULD** | API/network error handling | +3 | +3 | 0 | +3 | +3 |
| **SHOULD** | Read-only OAuth scope | +3 | +3 | +3 | +3 | +3 |
| **SHOULD** | Caching OAuth tokens across runs | +3 | +3 | +3 | +3 | +3 |
| **SHOULD** | Browser-based OAuth consent flow on first ru… | +3 | 0 | +3 | 0 | +3 |
| **COULD** | Automatic token refresh on expiry | 0 | +1 | +1 | +1 | 0 |
| **COULD** | Interactive query prompt as fallback when no… | 0 | 0 | 0 | 0 | 0 |
| **COULD** | Dependencies: gmail API libraries | +1 | +1 | +1 | +1 | +1 |
| **COULD** | Dependency: `argparse` for CLI argument pars… | 0 | 0 | 0 | 0 | 0 |
| **COULD** | Excluding `credentials.json` and `token.jso…` | 0 | 0 | 0 | 0 | 0 |
| **COULD** | Attachment downloading as explicitly out of… | +1 | +1 | +1 | +1 | +1 |
| **COULD** | Pagination as explicitly out of scope | +1 | +1 | +1 | +1 | +1 |
| **COULD** | Multiple Gmail accounts as explicitly out o… | +1 | +1 | +1 | 0 | 0 |

**Notes:**

- **Google Cloud setup (+5 for all):** All five acknowledge GCC credentials/setup as a prerequisite but none describe the steps to enable the API or create Desktop App credentials.
- **comp-2, server-side result count limit (−3):** "Attachment Detection" explicitly describes fetching up to 20 messages and reporting 3 from those 20 — client-side truncation, directly contradicting the criterion. The other four state a 3-result limit without naming the mechanism, earning +2 partial.
- **comp-1/3/4/5, server-side result count limit (+2):** All state a 3-result limit but don't name `maxResults` as the API parameter or explicitly distinguish server-side from client-side.
- **comp-2, browser OAuth flow (0):** No mention of a browser-based consent flow anywhere in the spec.
- **comp-4, browser OAuth flow (0):** Authentication section describes token caching and auto-refresh but never mentions a browser opening on first run.
- **comp-1, automatic token refresh (0):** "Stale `token.json` is auto-deleted and OAuth is re-triggered" describes deletion and re-authentication, not silent token refresh. comp-2, comp-3, comp-4 all explicitly say "auto-refreshed when expired."
- **comp-5, automatic token refresh (0):** "Expired/invalid token: auto-delete `token.json` and re-authenticate" — same pattern as comp-1: deletion + full re-auth, not silent refresh.
- **comp-3, error handling for missing credentials.json (+1):** "On auth failure: print error and exit non-zero" is generic and doesn't single out the missing-credentials case or mention setup instructions.
- **comp-3, API/network error handling (0):** "On auth failure" covers only OAuth/credential failures; no mention of catching API or network errors.
- **comp-4/5, multiple accounts out of scope (0):** Neither spec's out-of-scope section mentions multiple accounts.

### Summary

| Tier | comp-1 | comp-2 | comp-3 | comp-4 | comp-5 |
|---|---|---|---|---|---|
| Must (out of 6) | 5+ 1± | 5+ 1± | 5+ 1± | 5+ 1± | 5+ 1± |
| Should (out of 8) | 7+ 1± | 6+ 1- | 5+ 2± | 6+ 1± | 7+ 1± |
| Could (out of 8) | 4+ | 5+ | 5+ | 4+ | 3+ |
| Total points (92 max) | 82 | 75 | 78 | 79 | 81 |
| **Score** | **89%** | **82%** | **85%** | **86%** | **88%** |
