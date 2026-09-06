---
name: iterative-structured-spec
description:
  Iteratively write a specification based on a user request, sized to its complexity.
  Uses the why-what-how-unknowns high level structure.
---

## Instructions

- start by exploring the project and assessing the complexity of the request
- identify biggest sources of uncertainty and clarify them with the user
  - only ask about things that are hard to reverse and cannot be inferred
  - prefer using AskUserQuestion tool over in-conversation questions
- estimate spec size in words - pick one of the following:
  130, 200, 300, 500, 800, 1300, 2000, 3000, 5000, 8000.
- ask the user whether they want to go with that size or a different one -
  AskUserQuestion with 4 options (estimated, 2 below and 1 above)
- write iteratively: up to 1000 words at a time, and proceed to the next chunk
  after getting user's approval on what you wrote
- inferability principle: write only what cannot be derived from other stated
  content

## Spec structure

Organize the spec into the following toplevel sections: motivation, requirements,
approach (optional) and unknowns. Subsections are up to you. Below are guidelines
on where to put what (the spec doesn't have to cover all mentioned aspects).

**Motivation** - "why?"

- problem statement
- user intent / purpose
- goal / objective
- use-cases

**Requirements** - "what?"

- desired behavior / functional requirements
- out of scope / non-goals
- non-functional requirements
- constraints
- priorities
- acceptance / testing criteria

**Approach** - "how?" (optional)

- key design choices
- architecture
- trade-offs
- testing strategy
- rejected alternatives
- non-trivial dependencies

Don't describe implementation details here! Stay high-level.

**Unknowns**

- assumptions (never skip this!)
- risks
- open questions
- anything else that introduces uncertainty

**Cross-cutting aspects**

Items below could fit either in Requirements and/or in Approach - you decide:

- required setup / external dependencies
- error handling / failure modes
- edge cases and boundary conditions
- input validation
- security
- performance / scalability
- backward compatibility / public API changes

## Output size

- Be terse.
- Rewrite the spec using tighter prose to make it as short as possible.
- The spec should fit in the word count budget agreed with the user.
- If over the limit, drop the lowest-impact, highest-inferability content.