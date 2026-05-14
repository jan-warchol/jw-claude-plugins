---
name: iterative-problem-clarification
description: Iteratively ask questions about the most ambiguous aspects of the task you are about to handle. Use when handling tasks where not everything is clear.
---

This skill drives a process that will help you to effectively resolve ambiguities in the tasks you are given.

The process outline is as follows:

- Collect a few most important questions **and write them into a file**,
- Pick 1-2 questions that have most impact on the task,
- Ask these chosen questions with AskUserQuestion tool,
- **Write the answers down in another file**,
- Rinse and repeat until all important ambiguities are resolved.

## Notes directory

Directory .catnip/clarification-notes is at your disposal. You are free to create it if missing, run ls on it, and user Write and Read tools inside it - all these actions will be automatically allowed.

Please invoke mkdir and ls in separate tool invocations - the hook is not smart enough to handle and clear complex bash commands, it just looks for `mkdir [-p] .catnip[/clarification-notes]` and for `ls [options] .catnip/clarification-notes`.

Any filenames written in this skill file will implicitly mean files inside .catnip/clarification-notes.

## Current process ID

If this is the first iteration for current task, assign an ID to the current task and write it to `current-task-id` file. This ID is only for you, but writing it down should help you track the ID better.

## Prepare the questions

Think about the most ambiguous aspects of the task at hand. Prioritize the questions that have most impact on the
task scope, on the methods/techniques applicable to the task, and general task shape.

Take into account the answers already given by the user.

List up to 10 such questions and write them down in `<current-task-id>--<iteration number>--questions.md` file.

Don't limit yourself to technical questions. If the motivation for the task may have key impact on how it should be
handled, add questions about the problem that the user is trying to solve, e.g. what will be the intended audience
for the result, is this solving a production issue or just exploratory, etc. If you suspect a likely XY problem in
task formulation, you can add questions to clarify that.

Don't actually ask the questions before they are written down into the file.

If the task is completely clear and there are no questions to ask, just finish the skill.

## Pick the question(s) to ask first

Once you have the list, re-evaluate the questions importance and pick the most important one. The priorities for this choice are:

- The question resolves most ambiguity,
- The question and the recommended answer don't depend on the answers to other quesions,
- How simple the question is to answer for the user. If asking other questions first could guide the user to make
  more informed decision, prioritize these other questions.

If there are 2 questions that are very much independent, you can pick them both for a single AskUserQuestion iteration. If there is dependency, limit yourself to a single question.

If all the questions left are fairly trivial and don't require much thinking from the user, you can ask 3 or 4
questions at once. However, at that point you should consider whether asking these questions is really that important.

If the most important question is too open-ended to fit possibilities into 4 options, consider breaking it down into
2 or more questions. If you can break it down into 2 perpendicular questions, ask them in a single AskUserQuestion
call. If the partial questions depend on each other, ask first part with one AskUserQuestion call, then decide
on the exact form of the second question and ask it with another AskUserQuestion call. In such case never pick more
questions from the list, just the one you are breaking down.

## Check recursion depth

Check how many answers you have already asked about this topic and consider whether the next question is important
enough to ask. You should aim for only 1-2 questions for easy tasks, 4-8 questions for medium tasks, and up to 16
questions for complex tasks. However, this is not a hard limit, and if the task really needs clarification, you are
allowed to ask more questions.

If you decide that the answers given so far make picture clear enough to skip the rest of the questions, finish the skill without asking more questions.

## Ask the questions

Invoke AskUserQuestion tool with the question(s) you picked for this iteration.

## Write the answers down

Write the answers to the file `<current-task-id>--<iteration number>--answers.md` in Q&A format like:

```
**Q**: What is the intended audience for this specification?
**A**: Me and the AI agent that will implement it.

**Q**: What color should be the button?
**A**: Red.
```

## Invoke another iteration

Invoke another iteration of /iterative-problem-clarification skill to continue asking the questions.
