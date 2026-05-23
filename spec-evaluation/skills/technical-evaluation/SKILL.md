---
name: evaluate-spec-according-to-aggregated-points
description:
  Evaluates spec, comparing it to a list of criteria tiered into required, optional, and forbidden.
---

Given a spec and a list of key points (criteria) in tiers: Must, Should, Could, Should not, Must
not, score the spec fidelity to the criteria.

## Inputs

You should get file paths to the criteria file and one or more spec files. If you don't get them,
immediately ask for these paths and continue only after getting them.

## Criteria - scoring

Criteria succinctly describe the expected contents of the spec. Your task is to assign a score for
each of the criteria.

The value depends on which section the criterion belongs to. Use the following scoring:

| Tier               | Point value                        |
| ------------------ | ---------------------------------- |
| Must mention       | 10                                 |
| Should mention     | 3                                  |
| Could mention      | 1                                  |
| Should not mention | -3 (negative points when present)  |
| Must not mention   | -10 (negative points when present) |

For each of the criteria, check whether the spec mentions the issue it is about and whether it's
meaning is consistent with the expectation.

A mention must substantively address the concept the criterion describes. Incidental use of related
terms in a different context does not qualify — e.g. naming a service as a file's download source is
not the same as acknowledging that setup in that service is required. Parenthetical content in
criteria is for clarifying the concept's meaning, it's not a definitive checklist of required
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

## Text shortening method (used in tables)

Shorten each criterion text as follows: first remove any parenthetical content (text in parentheses
including the parentheses themselves), then if the remaining text is still longer than 45
characters, trim it to 44 characters and append `…`.

Examples:

- `Error handling for missing credentials (message with setup instructions)` →  
  `Error handling for missing credentials`  
  (parenthetical removed, under 45 chars — no trimming needed)
- `Read-only OAuth scope for minimum privilege access when connecting` →  
  `Read-only OAuth scope for minimum privilege …`  
  (no parenthetical, but over 45 chars — trimmed to 44 + ellipsis)

## Result

Print:

- A full table with columns: tier, criterion text (shortened as above), and one score column per
  spec. Use the filename without path or extension as the column header; if the filenames are long,
  shorten them or label them with letters. Include a mapping to full file paths (relative to project
  dir) before the table. Example:

  | Tier       | Criterion                   | plan-a | plan-b | plan-c |
  | ---------- | --------------------------- | ------ | ------ | ------ |
  | **MUST**   | Foobar is required input    | +10    | +10    | 0      |
  | **MUST**   | Frobnicator must not throw… | +10    | -10    | +10    |
  | **SHOULD** | consectetur adipiscing elit | +3     | 0      | +3     |

- Notes on any non-obious score assignments

- A summary table showing, for each spec, how many criteria per tier scored positively (e.g. fully
  matched "must"), partially (e.g. partially matched "must") and negatively (e.g. matched "must
  not", contradicted "must"), plus the overall score and percentage. Row headers name the tier and
  its total criterion count. Cell values show positive (+), partial (±) and negative (-) counts
  separately; if any count is zero, omit it. The "Total points" row header should include the max
  possible points in parentheses.

  Example:

  | Tier                  | plan-a  | plan-b   | plan-c  |
  | --------------------- | ------- | -------- | ------- |
  | Must (out of 5)       | 5+      | 2+ 2± 1- | 3+ 2-   |
  | Should (out of 10)    | 10+     | 7+       | 9+      |
  | Could (out of 8)      | 6+      | 4+       | 5+      |
  | Total points (88 max) | 86      | 51       | 74      |
  | **Score**             | **98%** | **58%**  | **84%** |

Please do not add anything else unless asked.
