---
name: evaluate-spec-according-to-aggregated-points
description: Evaluates spec, comparing it to an aggregated list of points tiered into required, optional, and forbidden.
---

Given a spec and a list of key points in tiers: Must, Should, Could, Must not, Should not, score the spec fidelity to the aggregated points.

## Inputs

You should get file paths to the spec file and the aggregated points file. If you don't get them, immediately ask for these paths and continue only after getting them.

## Aggregated points - scoring

Aggregated points succinctly describe the expected contents of the spec. Your task is to assign a score for each of the points.

The value depends on which section the point belongs to. The aggregated points file may suggest different point weights - disregard them. Use the following scoring:

| Tier               | Point value                        |
| ------------------ | ---------------------------------- |
| Must mention       | 10                                 |
| Should mention     | 3                                  |
| Could mention      | 1                                  |
| Must not mention   | -10 (negative points when present) |
| Should not mention | -3 (negative points when present)  |

For each of the points, check whether the spec mentions the issue the point is about and whether it's
meaning is consistent with the expectation.

For positive tiers (Must/Should/Could), the score is:
- Full points when the point is mentioned and consistent with the expectation,
- No points if the issue is not mentioned at all,
- Negative full points if the spec contradicts the point.

For negative tiers (Must not/Should not), the score is:
- Full points (negative) if the point is mentioned,
- No points otherwise (there are no positive points possible for negative tiers).

The total score is the sum of all point scores.

## Result

Please print:

- a full table containg columns for: actual score, tier, point text (summarize or cut with ellipsis points that would take more than 3 lines). It should look something like this:

        | Score | Tier | Point text |
        |------|-------|-------|
        | +10 | **MUST** | Foobar is required input |
        | +10 | **MUST** | Frobnicator must not throw exceptions |
        | 0 | **MUST** | Lorem ipsum |
        | -10 | **MUST** | Dolor sit amet |
        | +3 | **SHOULD** | consectetur adipiscing elit |


- 3-part list of the points with the scores: accepted points, missed points, contradicted points. Divide points in each of the list in subsections for each tier. For negative tiers, put them in Contradicted list (rather than Accepted) when found. Shorten the points text like in the table if necessary.

    The result should look something like the following:

        ### Accepted points

        - Must
          - Use OAuth auhentication (+10)
        - Should
          - Use `frobnicate` library (+3)

        ### Missing points

        - Could
          - Eat ice cream for breakfast (0)

        ### Contradicted points

        - Must
          - Handle errors by printing whole Lorem ipsum to stderr (-10)
        - Must not
          - Allow user to shot themselves in the foot (-10)

If a section has no points to show, fill it with `_(none)_`, like

        ### Missing points

        _(none)_

- Max possible score in form like:

        **Max possible score**: 80 (Must: 8 × 10) + 24 (Should: 8 × 3) + 8 (Could: 8 × 1) = **112**

- The actual total score in form like

        **Actual score**: 60 + 3 + 4 = **67**

Please do not add anything else and don't add extra headers between the output parts.
