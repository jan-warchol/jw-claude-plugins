---
name: write-specification
description: Create a specification based on the complexity of the user request.
disable-model-invocation: true
---

This skill requires two inputs: user request and optional word count limit.

## Analysis and clarifications

Start by analyzing user request and identifying the biggest sources of uncertainty (risks,
assumptions, ambiguity, missing information). Use AskUserQuestion tool to clarify the most important
points and confirm most important design decisions with the user. Ask betweem 1 and 7 questions,
dependon on the complexity of the task.

## Spec writing

Then write the specification according to the following guidelines:

- use 4 topelvel sections: goal, behavior, solution, unknowns
- use subsections freely, according to your judgement
- try to describe the behaviour separately from the implementation
- use specific, verifiable criteria to describe desired behavior
- state key design choices and rejected alternatives (if any)

## Output size

Use terse prose, avoid padding. The size of the spec should correspond to the request complexity.
Finally, If the user specified a word count, ensure that the specification is within the limit.

Save the spec as a markdown file.
