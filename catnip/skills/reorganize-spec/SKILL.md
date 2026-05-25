---
name: reorganize-spec
description: >
  Reorganize an existing spec so that sections make the most sense.
  Third step in the iterative spec-writing workflow.
---

Extend an existing spec by identifying and filling gaps in coverage. Second step of the workflow.

## Input

The argument may be:

- **A directory path** (passed by `iterative-spec-writing`): read `enriched.md` from that directory.
- **A file path**: read that file directly.
- **Nothing provided**: ask the user for the spec file path.

## Procedure

Analyze how the spec is organized into sections. Consider:
- whether some sections should be merged,
- whether information should be distributed in a different way
- whether there is duplicated information in different places
- whether sections could be grouped into subsections

## Output

Write the reorganized spec as `reorganized.md` in the same directory as the input file.
