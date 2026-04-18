---
name: assessing-complexity
description: Evaluate the complexity of each user request on a 1-10 scale to determine how thoroughly it should be handled.
---

Each time the user makes a request, start by assessing its complexity on a 1-10 scale.
Do it for all new tasks, not for follow-up requests that are clearly part of the same task.

Examples:

- **Level 1**: Simple questions, straightforward edits to a single file.
  1-10 lines of output, no reasoning required.
- **Level 3**: Changes across several files, simple self-contained script
  using one external API or a question requiring some research.
  10-100 lines of output, reasoning required.
- **Level 5**: Complete implementation of a single moderately complex feature
  in a software project, including writing tests and updating documentation.
  100-1000 lines of output.
- **Level 10**: Designing and implementing a complex software project.
  30,000+ lines of expected output, extensive reasoning and planning.

Don't include the cost of reading the files in the complexity rating. Be conservative
in your estimates; higher ratings should be used only when necessary. Err on the side
of lower ratings.

Output "Request complexity:" with your rating and a 6-18 word rationale.

Then log it by running this Bash command (with actual values substituted):

```
echo '{"rating":<N>,"input":"<user prompt>","rationale":"<your rationale>"}' > .cc-current-task-complexity.json
```
