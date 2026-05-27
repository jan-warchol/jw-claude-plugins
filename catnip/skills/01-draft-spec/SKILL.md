---
name: 01-draft-spec
description: Draft a spec. First step in the iterative spec-writing workflow.
---

Write an initial version of a spec for the user's request. This is the first step in an iterative workflow.

## Outline structure

Please use the following top-level structure:

- Objective: what are we building (short objective statement + motivation/background if available)
- Requirements (what it must do; what it shouldn't do)
- Solution (how are we about to do that; put technical decisions here that)
- Alternative solutions considered (if relevant)
- Out of scope
- Uncertainty

## Mention key assumptions

If you make assumptions that would have significant effect on the spec
if they turn out false or inaccurate, always note them explicitly.
That includes both assumptions about available tools and solutions (APIs, libraries)
and assumptions about user's intentions.

## Output

`initial.md` in the process directory.
