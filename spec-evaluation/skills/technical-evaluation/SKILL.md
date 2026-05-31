---
name: technical-evaluation
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
| Should mention     | 4                                  |
| Could mention      | 1                                  |
| Should not mention | -4 (negative points when present)  |
| Must not mention   | -10 (negative points when present) |

Score every criterion in two explicit steps. **Do not skip step 1** — writing down the stance
before the number is what keeps a contradiction from being mis-scored as an absence, and keeps
partial credit consistent across runs.

### Step 1 — Record the spec's stance (mandatory)

For each criterion, find where the spec addresses the criterion's **core concept** and record its
stance, with a short quoted snippet (or `—` when silent):

- **AGREES** — the spec addresses the core concept consistently with the expectation.
- **SILENT** — the spec does not address the concept at all.
- **CONTRADICTS** — the spec addresses the concept but takes the *opposite* position. A spec that
  quietly *does the opposite* is CONTRADICTS, not SILENT — you do not need an explicit rebuttal.

Judge the stance on the criterion's **core concept only**. Parenthetical and secondary details in a
criterion clarify what the concept means; they are **not** a checklist. Omitting — or even rejecting
— a secondary detail does not change the stance; only the position on the core concept does.
Incidental use of related terms in an unrelated context is not addressing the concept (e.g. naming a
service as a download source is not acknowledging that setup in that service is required).

Pick one dominant stance per criterion: if the spec gets the core right but rejects a *secondary*
element, the stance is AGREES; if it rejects the *core*, the stance is CONTRADICTS even when some
secondary element is present.

### Step 2 — Assign the score from the stance

For positive tiers (Must / Should / Could):

| Stance | Score |
| ------ | ----- |
| CONTRADICTS | negative full points (Must −10, Should −4, Could −1). **Never 0 for a contradiction.** |
| SILENT | 0 |
| AGREES — core fully conveyed | full points (Must 10, Should 4, Could 1) |
| AGREES — but a **core** element is missing (awareness shown, substance incomplete, e.g. mentions a file exists but not that it must be created/obtained) | partial = exactly half: Must = 5; Should = 2; Could has no partial → 0. A single partial value per tier — there is no finer gradation. |

Partial credit is only for a missing *core* element, never for a missing parenthetical/secondary
detail (that stays full).

For **Could** criteria that bundle several listed sub-features, substantially addressing the core
concept earns the full point — do not require every listed sub-feature to be present. Could is
full-or-nothing, but "full" means the core concept is covered, not that every sub-detail is.

For negative tiers (Must not / Should not):

- Negative full points (Must not −10, Should not −4) if the spec mentions or does the thing,
- 0 otherwise (there are no positive points for negative tiers).

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
  | **SHOULD** | consectetur adipiscing elit | +4     | 0      | +4     |

- Notes on non-obvious score assignments. Every CONTRADICTS (negative score) and every partial
  must appear here as a one-line `stance — "quoted snippet" — score` entry, so the direction of
  meaning is auditable.

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
