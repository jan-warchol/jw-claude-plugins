---
name: evaluate-spec-structure
description:
  Evaluates the structural quality of one or more specs — word count, parsability metrics, and
  presence of expected sections. Supports comparing multiple specs side by side.
---

# Spec Structure Evaluation

Analyze the structure and composition of one or more spec files and produce a report.

## Inputs

You need one or more spec file paths. If not provided, ask for them before continuing.

## Evaluating structure

Assess the structure of the document — does the spec cover areas listed below, and how well does it
do that? For each area, assign a score according to the criteria below.

Use semantic judgment when checking for sections — topic names are descriptions of intent, not exact
keywords; match by meaning. Sections can be named differently — a heading like "What we're not
building" counts as a dedicated section for "Out of scope."

### Goal (0—3 points)

Is the objective the user wants to achieve stated clearly?

| Score | Assign when                                                            |
| ----- | ---------------------------------------------------------------------- |
| 3     | There is a dedicated section with a concrete, specific statement       |
| 2     | Goal is specific and explicitly stated but without a dedicated section |
| 1     | Goal can be clearly inferred from context but isn't directly stated    |
| 0     | Goal is absent or too vague to act on                                  |

Note: a document that opens with the spec title as the top-level heading and states the goal clearly
in the first sentence/paragraph counts as score 3.

### Requirements (0—3 points)

Is there a clear list of verifiable success/acceptance/testing criteria?

Verifiable means: each criterion can be objectively evaluated as pass/fail. Vague qualities like
"fast", "easy to use", or "reliable" are not verifiable unless accompanied by a specific measurable
threshold (e.g. "response time under 200 ms", "error rate below 0.1%").

| Score | Assign when                                                                      |
| ----- | -------------------------------------------------------------------------------- |
| 3     | There is a dedicated section with specific, verifiable criteria                  |
| 2     | Criteria are listed without a dedicated section, and at least 2/3 are verifiable |
| 1     | Criteria are mentioned but most of them are vague                                |
| 0     | No specific criteria; hard to tell whether the spec is satisfied                 |

### Solution (0—4 points)

Score = sum of all that apply:

- 0–2 for solution overview and design decisions:
  - +2 if the solution and key design decisions are clearly articulated (dedicated section, stated
    explicitly)
  - +1 if a solution or design decisions are present but implicit, or scattered across the document
- +1 if priorities or trade-offs are discussed (what should be sacrificed for what)
- +1 if alternative solutions are mentioned with reasoning for why they were rejected

### Out of scope (0—3 points)

Does the spec discuss what is explicitly excluded?

| Score | Assign when                                                            |
| ----- | ---------------------------------------------------------------------- |
| 3     | There is a dedicated section listing explicit exclusions               |
| 2     | Exclusions are listed but without a dedicated section                  |
| 1     | Scope boundaries are implied or mentioned in passing, but not explicit |
| 0     | No mention of what is excluded or intentionally deferred               |

### Uncertainty (0—4 points)

Does the spec discuss what is uncertain, e.g. assumptions, risks, open questions?

Score = sum of all that apply:

- +1 if risks are discussed
- +1 if assumptions are explicitly listed
- +1 if open questions or unknowns are explicitly listed
- +1 if there is a dedicated section (or sections) for these

## Computing composition metrics

Run `measure.py` using `uv run` from the `spec-evaluation` plugin directory (the one containing
`pyproject.toml`). This ensures dependencies are installed automatically into the project's virtual
environment.

```
uv run --project /path/to/spec-evaluation \
    python /path/to/spec-evaluation/skills/evaluate-spec-structure/measure.py \
    spec1.md spec2.md ...
```

To find the plugin directory, locate `pyproject.toml` starting from this SKILL.md's directory and
walking up. The script is at `skills/evaluate-spec-structure/measure.py` relative to that directory.

It outputs a JSON array with one object per file. Use the values from there directly — do not
recompute them manually. The fields are:

| JSON field            | Metric                                                                              |
| --------------------- | ----------------------------------------------------------------------------------- |
| `word_count`          | Total words (all content, including inside code blocks)                             |
| `avg_section_len`     | Mean words per section (content between headings)                                   |
| `avg_paragraph_len`   | Mean words per paragraph-level block; a whole list or table counts as one paragraph |
| `avg_bullet_len`      | Mean words per individual list item (direct content only, not sub-lists)            |
| `code_char_ratio_pct` | % of document chars inside code spans (fenced blocks + inline code)                 |

## Output

Use the filename without path or extension as the column header. If filenames are long, shorten them
or, if they are ambiguous, label them with letters (A, B, C…). Include the mapping to full paths
before the table.

### Topics comparison table

One row per topic plus a Total row, one column per spec. Cells show the numeric score.

```
| Topic | spec-a | spec-b | spec-c |
|-------|--------|--------|--------|
| Goal | 3 | 2 | 3 |
| Requirements | 2 | 0 | 3 |
| Solution | 3 | 1 | 2 |
| Out of scope | 3 | 1 | 0 |
| Uncertainty | 4 | 2 | 3 |
| **Total (max 17)** | **15** | **6** | **11** |
```

Include notes on non-obvious score assignments only. Do not explain scores that match the rubric
straightforwardly.

### Metrics comparison table

```
| Metric | spec-a | spec-b | spec-c |
|--------|--------|--------|--------|
| Word count | 342 | 198 | 501 |
| Avg section length | 49.1 | 33.0 | 61.4 |
| Avg paragraph length | 21.5 | 18.2 | 24.7 |
| Avg bullet length | 8.4 | 11.2 | 6.1 |
| Code snippets ratio | 18% | 0% | 31% |
```
