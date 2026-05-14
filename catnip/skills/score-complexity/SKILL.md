---
name: score-complexity
description: Assign complexity score to a task to better assign the amount of effort required to address it and estimate the expected output size.
---

Assess the complexity of the task at hand.

## Available complexity scores

- Trivial:
    - Task is short, self contained, and doesn't require any research.
    - Mainly assign this level to questions that can be answered just based on your knowledge and context. If any reasearch is required, the task is not trivial.
    - There is no ambiguity and the task can be performed without requiring any clarification.
    - It results in a single, small artifact (answer, file, command execution).
- Simple:
    - Task is short, and requires limited research (e.g. looking up 1-2 project files, single web search) or no research at all.
    - Mainly assign this level to questions and tasks that can be done quickly, with limited research. No plan is required.
    - There is limited ambiguity. There are at most 1-2 key questions to be asked to resolve most of the ambiguity.
      A few more questions about details may be allowed to improve precision, but if there are more than 2 "large"
      quesions, the complexity should be bumped up.
    - These tasks would usually result in a single artifact of moderate size.
- Medium:
    - Task description can be longer and refer to external knowledge. It may require some more research (several lookups of the files and/or web).
    - The tasks at this level require some consideration and possibly a few iterations. Having a stated plan, even
    though short, would be helpful.
    - More ambiguity is allowed. This kind of task may require several key questions and may need a handful of detail
      clarifications to get everything right.
    - The task may result in producing several artifacts and/or performing multiple actions. The result could be
      e.g. a complete (small) React application, a moderate sized script, a specification for a small feature.
- Large:
    - Task description may be long and have many references. The task would typically require some research - looking
      up existing codebase, documentation, references, searching the web - and extended expert knowledge.
    - Significant reasoning effort is required and the task would usually require a few iterations - either directly,
      or the output would be expected to need several refinement rounds.
    - Ambiguity may be large and may require 10+ significant questions to be answered, and many more to iron out
      the details (often left to be addressed in further iterations).
    - The output may be large and contain many files or result in several different actions being performed, though
      it still can be realized within a single session.
- Extra large:
    - Task cannot be effectively executed in a single iteration and needs to be broken down into several Medium-Large size tasks, or even into other Extra large tasks in extreme cases.
    - This category extends all the way to most complex tasks.
    - Ambiguity may be extreme and generally wouldn't be resolvable during single session, but would rather require
      dedicated subtasks to research and resolve.
    - Expected output for the single session would usually be some task breakdown and outline plan for execution, and
      perhaps a stub of the final result (e.g. a skeleton implementation of an application, or story outline for a novel).

## Reconciling differences across the axes

Some tasks may match different categories across different axes - e.g. a task may have little ambiguity, but require
a very large output, or require a huge, multi-stage research but produce a single number as the result. Usually
the highest score would be still best suited. Use your judgement to decide.

## Output

Write just a single sentence:

```
Task complexity category: <category name>
```

Do not add the rationale for your decision. Don't add any more labels, headers, or styling.
