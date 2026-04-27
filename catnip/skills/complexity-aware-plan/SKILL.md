---
name: complexity-aware-plan
description: Create a plan based on the assessed complexity of the user request.
---

Start by invoking `assessing-complexity` skill if you haven't done already.
Analyze user request and prepare the action plan.

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

If the complexity is 3 or more:
- include explicit non-goals (or "out of scope") in the plan
- ask the user 1-2 questions clarifying the most important design decisions (use AskUserQuestion tool)

If the complexity is 5 or more:
- explicitly list risks and assumptions in the plan
- ask the user 3-5 questions about the most important risks and assumptions (use AskUserQuestion tool)

Save the plan as a markdown file ending with `-plan.md` in project root directory (unless
the user specified otherwise).
