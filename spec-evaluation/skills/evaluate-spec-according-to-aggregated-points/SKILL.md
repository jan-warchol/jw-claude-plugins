---
name: evaluate-spec-according-to-aggregated-points
description:
  Evaluates spec, comparing it to a list of criteria tiered into required, optional, and forbidden.
---

Given a spec and a list of key points (criteria) in tiers: Must, Should, Could, Must not, Should
not, score the spec fidelity to the criteria.

## Inputs

You should get file paths to the criteria file and one or more spec files. If you don't get them,
immediately ask for these paths and continue only after getting them.

## Criteria - scoring

Criteria succinctly describe the expected contents of the spec. Your task is to assign a score for
each of the criteria.

The value depends on which section the criterion belongs to. The criteria file may suggest different
weights - disregard them. Use the following scoring:

| Tier               | Point value                        |
| ------------------ | ---------------------------------- |
| Must mention       | 10                                 |
| Should mention     | 3                                  |
| Could mention      | 1                                  |
| Must not mention   | -10 (negative points when present) |
| Should not mention | -3 (negative points when present)  |

For each of the criteria, check whether the spec mentions the issue it is about and whether it's
meaning is consistent with the expectation.

A mention must substantively address the concept the criterion describes. Incidental use of related
terms in a different context does not qualify — e.g. naming a service as a file's download source is
not the same as acknowledging that setup in that service is required. Parenthetical content in
criteria is for clarifying the concept's meaning, it's not a definitivs checklist of required
details.

For positive tiers (Must/Should/Could), the score is:

- Full points when the issue is mentioned and consistent with the expectation,
- Half points when the concept is partially addressed — the spec shows awareness but misses a key
  element (e.g. mentions a file exists but not that it must be created/obtained). For Must, half is
  exactly 5. For Should, half is 1.5 — round to 1 or 2 based on how much of the concept is covered.
  Could criteria have no partial credit: score 0 if not fully addressed.
- No points if the issue is not mentioned at all,
- Negative full points if the spec contradicts the criterion.

For negative tiers (Must not/Should not), the score is:

- Full points (negative) if the issue is mentioned,
- No points otherwise (there are no positive points possible for negative tiers).

The total score is the sum of all point scores.

## Criteria text shortening (used in all tables)

Shorten each criterion text as follows: first remove any parenthetical content (text in parentheses
including the parentheses themselves), then if the remaining text is still longer than 50
characters, trim it to 45 characters and append `…`.

For example:

- `Error handling for missing credentials.json (message with setup instructions)` →
  `Error handling for missing credentials.json` (parenthetical removed, under 50 chars — no trimming
  needed)
- `Server-side result count limit (maxResults API parameter, not client-side truncation)` →
  `Server-side result count limit` (parenthetical removed)
- `Read-only OAuth scope for minimum privilege access when connecting` →
  `Read-only OAuth scope for minimum privilege acces…` (no parenthetical, but over 50 chars —
  trimmed to 45 + ellipsis)

## Result — single spec

When evaluating a single spec, please print:

- A full table with columns: actual score, tier, criteria (shortened as above). Example:

        | Score | Tier | Criterion |
        |------|-------|-------|
        | +10 | **MUST** | Foobar is required input |
        | +10 | **MUST** | Frobnicator must not throw exceptions |
        | 0 | **MUST** | Lorem ipsum |
        | -10 | **MUST** | Dolor sit amet |
        | +3 | **SHOULD** | consectetur adipiscing elit |

- 2-part list of missed and contradicted criteria. Divide criteria in each section by tier. For
  negative tiers, put them in Contradicted (rather than Missing) when found. Shorten criteria as
  above.

  Example:

        ### Missing

        - Could
          - Eat ice cream for breakfast (0)

        ### Contradicted

        - Must
          - Handle errors by printing whole Lorem ipsum… (-10)
        - Must not
          - Allow user to shot themselves in the foot (-10)

  If a section has no criteria to show, fill it with `_(none)_`.

- Notes on any non-obious score assignments

- Max possible points, actual points, and percentage score:

        **Max possible points**: 80 (Must: 8 × 10) + 24 (Should: 8 × 3) + 8 (Could: 8 × 1) = **112**

        **Actual points**: 60 + 3 + 4 = **67**

        **Score**: 67 / 112 = **60%**

## Result — multiple specs

When evaluating multiple specs against the same criteria, please print:

- A full table with columns: tier, criterion text (shortened as above), and one score column per
  spec. Use the filename without path or extension as the column header; if the filenames are long,
  shorten them or label them with letters. Include a mapping to full file paths (relative to project
  dir) before the table. Example:

        | Tier | Criterion | plan-a | plan-b | plan-c |
        |------|------------|--------|--------|--------|
        | **MUST** | Foobar is required input | +10 | +10 | 0 |
        | **MUST** | Frobnicator must not throw… | +10 | -10 | +10 |
        | **SHOULD** | consectetur adipiscing elit | +3 | 0 | +3 |

- Notes on any non-obious score assignments

- A summary table showing, for each spec, how many criteria per tier scored positively (e.g. matched
  "must") and negatively (e.g. matched "must not", contradicted "must"), plus the overall score and
  percentage. Row headers name the tier and its total criterion count. Cell values show positive vs
  negative count separately; omit negative count when it is zero. The "Total points" row header
  should include the max possible points in parentheses. Example:

        | Tier | plan-a | plan-b | plan-c |
        |---|--------|--------|--------|
        | Must (out of 5) | 5 | 4 / -1 | 3 / -2 |
        | Should (out of 10) | 10 | 7 | 9 |
        | Could (out of 8) | 6 | 4 | 5 |
        | Total points (88 max) | 86 | 61 | 74 |
        | **Score** | **98%** | **69%** | **84%** |

Please do not add anything else and don't add extra headers between the output parts.
