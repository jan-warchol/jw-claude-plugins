---
name: complexity-aware-spec
description: Create a spec based on the complexity of the user request.
disable-model-invocation: true
---

This skill requires two inputs: user request and its complexity rating on a 1-10 scale. If the
rating was not provided as an argument, invoke `assessing-complexity` skill. Throughout this skill,
N will mean the complexity rating.

Before writing the spec, identify biggest sources of uncertainty (risks, assumptions, missing
information) and use AskUserQuestion tool to clarify the most important points and confirm most
important design decisions with the user. Ask between floor(N/2)-1 and 2×(N-1)-1 questions (e.g. 0-3
questions for complexity 3, 2-7 for complexity 5).

Document decisions when the user did not choose the recommended option.

## spec size and structure

The spec document must begin with YAML frontmatter containing these required fields:

```yaml
---
goal: <6-12 word description of the desired outcome>
prompt: <initial user prompt copied verbatim>
complexity: <1-10 scale>
project: <absolute path to project dir>
model: <agent model ID>
---
```

The size of the spec should correspond to the request complexity. Overall word count should be
between 50×(N-1) and 100×(N-1) words (e.g. 200-400 words for complexity 5). Note: only words with
letters count towards the limit - punctuation and markdown formatting such as ### 1. 2. |----| are
not counted, so you can use formatting freely.

## What to include in the spec

If the complexity is 2 or more:

- list success criteria / verification criteria (as bullet points) - the number of criteria must be
  between (N-1)²/3 and N².
- list implementation steps/phases

If the complexity is 3 or more:

- list non-goals / out of scope
- address error handling (if applicable)

If the complexity is 4 or more:

- include explicit problem statement
- list dependencies / setup requirements
- address security (if applicable)

If the complexity is 5 or more:

- address uncertainty (risks, assumptions, etc)
- address performance (if applicable)
- mention alternatives considered and why they were rejected
- address testing (if applicable)

Note: you **may** include aspects required in higher complexity in cases of lower complexity if you
consider them important. For example, you can list a significant risk in a complexity-3 task.

## Final notes

Save the spec as a markdown file ending with `-spec.md` in project root directory (unless the user
specified otherwise).
