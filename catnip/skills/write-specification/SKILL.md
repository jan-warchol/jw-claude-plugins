---
name: write-specification
description: Create a specification based on the complexity of the user request.
disable-model-invocation: true
---

This skill has two inputs: user request and optional word count limit.

## Procedure

Start by analyzing user request and clarifying the most important issues/decisions with the user.
Then write the spec, keeping in mind the desired structure described below. The size of the spec
should correspond to the request complexity. Finally, compress the output and save it as a
markdown file.

### Writing principle: inferability

Only state what cannot be derived from other stated content. Prefer principles and reasoning over
enumerating their consequences. A shorter spec that makes the logic clear is better than a longer
one that spells out its implications.

## Clarifications

Identify the biggest sources of uncertainty (risks, assumptions, ambiguity, missing information).
Use AskUserQuestion tool to clarify the most important items and confirm most important design
decisions with the user. Ask between 1 and 7 questions, depending on the complexity of the task.

Only ask about decisions that are both high-impact (hard to reverse, or would significantly shape
the solution) and high-uncertainty (not clearly implied by the request or existing code). Skip
questions about anything that can be easily changed later.

## Spec structure

Organize the spec into 4 toplevel sections (note: descriptions that follow these are guidelines,
not exhaustive checklists - include more content when needed). Organize content into subsections
freely. Use bullet points whenever possible.

### Goal

Short, clear and specific answer to the question "why?" - this may include:

- objective
- motivation/problem statement
- user intent
- use cases

### Requirements

This section should answer the questions "what the result should and should not do?" and "how does
successlook like? how does the failure look like?".

- desired behavior
- out of scope / non-goals
- functional and non-functional requirements
- use specific, verifiable criteria
- avoid implementation details (how things will be done) in this section

### Solution

Lay out the solution:

- overall approach
- key design choices
- architecture (if applicable)
- whether it's a breaking change (if applicable)
- priorities and trade-offs (if any)
- rejected alternatives (if any)
- non-trivial dependencies (if any)
- this is the section for discussing implementation

### Unknowns

Discuss uncertainty:

- assumptions
- risks
- open questions
- any other unknowns

## Output compression

Rewrite the spec using tighter prose. Eliminate any padding; check that no low-impact and
high-inferability items slipped in (content a reasonable agent could derive from the rest). Reduce
the word count as much as possible without losing information and with minimal impact on the
structure.

If the user specified a word count, check whether the specification is within the limit. If over
the limit, drop the remaining lowest-impact, highest-inferability content. Never drop entire
sections.
