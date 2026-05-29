---
name: contradiction-analysis
description:
  Compares one or more candidate specs against a reference spec and reports where they contradict it,
  separated into direct contradictions and weaker divergences/gaps. Use when you have an authoritative
  reference spec and want to find where generated/candidate specs conflict with it.
---

# Spec Contradiction Analysis

Given an authoritative **reference spec** and one or more **candidate specs**, find every place a
candidate states something that conflicts with the reference, and report them grouped by
contradiction. This is a fidelity check against a reference document.

## Inputs

- One **reference spec** file path (the authoritative document).
- One or more **candidate spec** file paths to check against it.

If the reference and candidate(s) are not clearly identified, ask which file is the reference before
continuing.

## What counts as a contradiction

Classify each finding into one of two tiers.

**Direct contradiction** — the candidate states behavior that conflicts with an *explicit*
requirement or statement in the reference. The reference says X; the candidate says not-X, or
specifies something that necessarily violates X.

**Weaker divergence / gap** — one of:

- a divergence from a reference *preference or intent* expressed in soft language ("ideally",
  "preferably", "leaning toward", "most likely");
- a questionable design choice that works against the reference's stated goal without flatly
  contradicting a hard rule;
- a reference requirement the candidate leaves **unaddressed** (silence on a required behavior).
  Label these clearly as gaps, not head-to-head conflicts.

Do **not** report as contradictions: stylistic differences, additions the reference is silent about
that don't conflict with anything, or anything covered under "Excluding scope/staging" below.

## Excluding scope/staging differences

Distinguish *whether/when a feature is included* from *how a feature behaves*.

If the candidate specs intentionally omit version/stage distinctions (e.g. the reference tiers
features into V0/V1/V2 but the candidates don't model stages), then a candidate including a
feature the reference defers to a later stage is **not** a contradiction. Exclude these.

When unsure whether a difference is purely scope/staging, ask the user, or report it but mark it as
scope-related so it can be filtered.

## Method

1. Read the reference spec thoroughly first. Note its hard requirements (imperative language: "must",
   "required", "always", "no X allowed") separately from soft preferences.
2. For each candidate, scan section by section for statements that conflict with the reference.
   Check both directions: explicit opposite claims, and choices that necessarily violate a reference
   rule.
3. Also note reference requirements the candidate never addresses (gaps → weaker tier).
4. For every finding, capture: the reference's position (with line numbers) and the candidate's
   wording (with section reference) so the conflict is independently verifiable.
5. De-duplicate across candidates: the same contradiction made by several candidates is **one**
   entry listing each offending candidate, not one entry per candidate.

## Output

Group **by contradiction**, not by candidate. Write a markdown report with:

1. A short header naming the reference and candidates.
2. A **Direct contradictions** section: numbered entries (`D1`, `D2`, …).
3. A **Weaker divergences / gaps** section: numbered entries (`W1`, `W2`, …).
4. A short **Cross-cutting patterns** section listing contradictions shared by all (or most)
   candidates — the strongest signal of what the reference is failing to convey.

Each entry follows this shape — reference position first, then one bullet per offending candidate:

```markdown
### D3. Drawing order: bands painted after lines
Reference (line 101): order is bands, lines, points.
- **spec-1** (line 134): strokes all series paths, then draws band fills → bands on top.
- **spec-3** (line 98): render loop strokes paths, then `drawBandFill(...)` → bands on top.
```

Conventions:

- Always cite the reference and the candidates by line number.
- Use the filename without path or extension to refer to each candidate; include a mapping to full
  paths once at the top if names are ambiguous.

Default output path: `contradictions.md` in the directory of the candidate specs (or the current
directory). Prompt before overwriting an existing file.

Do not add scoring, recommendations, or fixes unless asked — this skill reports conflicts only.
