---
name: complexity-aware-plan
description: Create a plan based on the complexity of the user request.
---

This skill requires two inputs: user request and its complexity rating on a 1-10 scale.
If the rating was not provided as an argument, invoke `assessing-complexity` skill.

Before writing the plan, identify biggest sources of uncertainty (risks, assumptions,
missing information) and use AskUserQuestion tool to clarify the most important points
and confirm most important design decisions with the user.
Ask at most 2×(n-2) questions, where n is the complexity rating
(e.g. max 2 questions for complexity 3, max 6 for complexity 5).


## Plan document structure

The plan document must begin with YAML frontmatter containing these required fields:

```yaml
---
goal: <6-12 word description of the desired outcome>
prompt: <initial user prompt copied verbatim>
complexity: <1-10 scale>
---
```

The size of the plan should correspond to the request complexity. Overall word count
should be between 50×(n-1) and 100×(n-1) words, where n is the complexity rating
(e.g. 200-400 words for complexity 5). Note: only words with letters count towards
the limit - punctuation and markdown formatting such as ### 1. 2. |----| are not
counted, so you can use formatting freely.


## What to include in the plan

Success criteria (as bullet points) - taking n as a basis, the number of criteria
must be between (n-1)²/3 and n².

If the complexity is 3 or more:

- explicitly list non-goals / "out of scope"

If the complexity is 5 or more:

- explicitly address uncertainty (risks, assumptions, etc)


## Final notes

Save the plan as a markdown file ending with `-plan.md` in project root directory (unless
the user specified otherwise).
