---
name: enrich-spec
description: >
  Enrich an existing spec by filling gaps in its coverage.
  Second step in the iterative spec-writing workflow.
---

Extend an existing spec by identifying and filling gaps in coverage. Second step of the workflow.

## Procedure

Evaluate the draft against the following checks:

- Is the objective clearly and specifically stated?
- Is the expected behavior described specifically enough to verify?
- Are key design choices explicitly stated?
- Are trade-offs and rejected alternatives discussed?
- Are explicit exclusions listed?
- Are risks, assumptions, and open questions discussed?

If a topic is already covered — even under a section with a different name — leave it as is.

Prefer expanding existing sections to adding new ones. When the checks turn up closely related
topics, keep them together under one section (using subsections if helpful), not split across
separate sections.

The enriched spec must not exceed 2× the draft's word count. Before saving, count the words
in your output; if over budget, cut the least important additions and re-check.
