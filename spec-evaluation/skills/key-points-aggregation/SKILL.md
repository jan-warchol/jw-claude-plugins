---
name: key-points-aggregation
description: Aggregates key points from a collection of plans or specs into a structured, tiered key points reference file. Use this skill when the user wants to extract, merge, or consolidate key points from multiple plan/spec documents into a single reference file with must/should/could/must-not tiers. Triggers include: "aggregate key points from plans", "create a key points file", "extract points from specs", "merge key points", "build a reference list from plans".
---

# Key Points Aggregation

Read one or more plan/spec files (or directories of them) plus an optional existing key points file,
and produce a consolidated key points reference file with tiered rankings. The goal is to produce
a checklist for evaluating plan/spec files.

## Input

- One or more file paths or directories (searched recursively for `.md`, `.txt`, `.rst`)
- Optional: an existing key points file in the output format below

## Output format

```markdown
# Key Points

## Must mention
- <point>

## Should mention
- <point>

## Could mention
- <point>

## Must Not mention
- <point>

## Should Not mention
- <point>
```

The **Must Not mention** and **Should Not mention** sections are never populated automatically — leave them empty. They are reserved for manual addition of content prohibitions.

Out-of-scope items belong in Must/Should/Could mention with negative framing, e.g. *"mobile support as explicitly out of scope"*.

## Tier definitions

Each tier answers the question: *should a good spec mention this?*

- **Must mention**: omitting this would lead to a materially different implementation
- **Should mention**: important, but a competent agent could plausibly infer it from context
- **Could mention**: easily inferable; low cost if missing
- **Must Not mention**: manually added only — never inferred from source documents

When in doubt, prefer a lower tier. It's easier to promote than demote. Sort items according to importance in each tier.

Implementation-specific details (a particular API method name, an exact file format, a specific scope string) generally belong at **Should** or **Could**, unless the implementation choice is itself the quality criterion — e.g., server-side vs. client-side filtering is a design criterion; which exact API method achieves it is not.

## Point formulation rules

Each point names a topic the spec should mention — not what it should say about it. The key points file is an evaluation rubric, not a spec.

**Framing**: write each point as a noun phrase. The section header ("Must mention", "Should mention", etc.) supplies the verb.

| ❌ Prescriptive (wrong) | ✅ Noun phrase (correct) |
|---|---|
| "Catch `HttpError`, print the error, and exit cleanly" | "API/network error handling" |
| "Use `maxResults=3` to limit at the API level" | "Result count limit at the API level (not client-side truncation)" |
| "Load credentials from `credentials.json`, cache token in `token.json`" | "`credentials.json` as OAuth client secrets file" + "`token.json` for token caching" |

A brief parenthetical is fine when it prevents ambiguity, as in the second example above. The parenthetical should clarify **what** the point covers, not **how** to implement it — `(not client-side truncation)` is a scope clarifier; `(exit code 1)` is an implementation prescription. Parentheticals are context for the evaluator to understand the concept; they are not a checklist of details that must appear verbatim in the spec.

**Outcome, not implementation**: A point should check whether a concern is addressed — not require a specific implementation approach. Avoid prescribing exact exit codes, specific library method names, or exact error message wording; those are for the spec author to decide. Name the concern, not the mechanics.

| ❌ Prescriptive (wrong) | ✅ Outcome-focused (correct) |
|---|---|
| "Missing `credentials.json`: clear error message + exit code 1" | "Error handling for missing `credentials.json` (message with setup instructions)" |
| "`messages.get` to extract headers and MIME part filenames" | "Per-message retrieval of headers and attachment filenames" |
| "No-results case: informative message + exit 0" | "Graceful handling when there are no results (informative message, no crash)" |

**Atomicity**: each point should be independently checkable. If a point bundles multiple facts that could each be present or absent separately, split it. Apply this even when source documents used compound statements.

## Workflow

1. Read all source plan/spec files
2. If an existing key points file is provided, read it and note its explicit tiers — these take precedence over your own judgment for points already present
3. In a single pass, synthesize all content into a unified key points list:
   - Merge points that express the same idea, even if worded differently
   - Formulate each point using the framing and atomicity rules above
   - Assign tiers using the definitions above
   - Order within each tier: more fundamental points first
4. Write the output file
   - Default path: `key-evaluation-points.md` in the current directory, or alongside the existing key points file if one was provided
   - Prompt before overwriting an existing file (unless it's the input key points file being updated)


## Edge cases

- Single source file: extract and tier directly, no merging needed
- Empty or unreadable files: skip with a warning
- Conflict between existing tier and your judgment: keep existing tier
