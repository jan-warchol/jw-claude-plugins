---
name: write-specification
description:
  Write a specification based on a user request, sized to its complexity. Intended for non-trivial
  requests.
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
decisions with the user. Ask 1-4 questions (1 for simple tasks, 4 for complex ones). For very
complex tasks, or when the user's answers require follow-up, ask a second round of 1-4 questions.

Only ask about decisions that are both high-impact (hard to reverse, would require a different
solution) and high-uncertainty (not clearly implied by the request or existing code). Skip
questions about anything that can be easily changed later. When you can pick a sensible default,
prefer recording it as an assumption (see Unknowns) over asking — reserve questions for decisions
where guessing wrong would be costly.

## Spec structure

Organize the spec into 4 toplevel sections (goal, requirements, design and unknowns). Note:
descriptions that follow are guidelines, not exhaustive checklists - include more content when
needed. Organize content into subsections freely. Use bullet points whenever possible.

### Goal

Short, clear and specific description of the objective. This may also include:

- problem statement (if provided)
- motivation / user intent / purpose (if provided)
- use cases (if provided)

**State only what was specified by the user** - don't add your own interpretations.

### Requirements

This section should answer the question "what" - "what should the result do?", "what should it not
do?", "what do success and failure look like?".

- desired behavior
- out of scope / non-goals
- functional and non-functional requirements

Use specific, verifiable criteria - make it easy to check whether a candidate implementation meets
the requirements. Prefer specifying measurable thresholds where possible. Don't put implementation
details in this section.

### Design

This is the section for discussing "how?" - the solution and implementation.

- overall approach
- key design choices
- architecture (if applicable)
- priorities and trade-offs (if any)
- rejected alternatives (if any)
- non-trivial dependencies (if any)

**Important:** avoid describing behavior in this section. All requirements must be documented in
`Requirements` section and its sub-sections.

### Unknowns

Discuss uncertainty:

- assumptions (never skip this!)
- risks
- open questions (if applicable)
- any other unknowns

### Cross-cutting concerns

Where applicable, also consider the items below. Each can be framed as behavior or as
implementation, so put it in whichever of the four sections above fits how you've framed it (e.g.
as a requirement under Requirements, or as a design choice under Design) — don't force it into a
fixed section, and don't add a section for these.

- required setup / external dependencies
- error handling / failure modes
- edge cases and boundary conditions
- input validation
- security
- performance / scalability
- backward compatibility / public API changes

## Output compression

Rewrite the spec using tighter prose. Eliminate any padding and remove anything that violates the
inferability principle above. Reduce the word count as much as possible without losing information
and with minimal impact on the structure.

If the user specified a word count, check whether the specification is within the limit. If over
the limit, drop the remaining lowest-impact, highest-inferability content. Never drop entire
sections.
