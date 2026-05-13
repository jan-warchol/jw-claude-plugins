---
name: prepare-eval-knowledge-file
description: Prepare knowledge file that will be used for planner evaluation
disable-model-invocation: true
---

This skill requires a prompt for plan/specification (the same thing that would be passed to catnip:complexity-aware-spec skill) and its complexity rating on a 1-10 scale. If not given both as skill arguments, immediately ask user for the missing pieces.

It can also get extra paths to files with more knowledge that catnip:complexity-aware-spec wouldn't get. These will be passed after the complexity score and are not part of the prompt.

You need to prepare to answer questions that an agent running catnip:complexity-aware-spec would ask the user with AskUserQuestion tool. Your task right now is to prepare for all questions that such agent would plausibly ask and write down the answers.

For all questions that are important and aren't answered by context files, you must ask user for the answer.
For other questions that don't have clear answers, you'll be able to pick or invent your own answers.

Remember that the agent will be only given the prompt (and files mentioned directly in the prompt), but not the extra knowledge files that you may be given, so that should be the base for thinking about the questions you may be asked.

## Questioning the user

Prepare up to 20 most important questions that don't have clear answer in the existing knowledge and query the user with AskUserQuestion tool. Write the questions and answers verbatim into the USER ANSWERS questions. If the user interrupts in order to write free form answer, take this answer and then get back to using AskUserQuestion tool.

## Preparing more answers

The idea is that you'll be able to answer any sensible question consistently, based just on this written down knowledge.

For any question you think the agent running catnip:complexity-aware-spec is likely to ask and that wasn't answered by the user or is not unabiguously answered by the extra context, write down the answer in PREPARED ANSWERS section.
Make it succinct, they just need to be long enough to resolve ambiguities consistently. Whether you write it down in Q&A format or just as list of decisions is up to you, as long as you'll be able to understand it without ambiguity.

The answers must not contradict any of the given knowledge and context.

## Preparing the output

The output is going to be a file looking like:

```
=== TASK (complexity <complexity score given>) ===
<initial prompt from the user + contents of files that you were asked to read, if any>
=== TASK ===

=== USER ANSWERS ===
These questions were answered directly by a human user.

<Q&A list with questions and answers given by user directly>
=== USER ANSWERS ===

=== PREPARED ANSWERS ===
These answers were prepared by AI agent in order to reduce ambiguity.

<Q&A list with questions and answers given prepared by you>
=== PREPARED ANSWERS ===
```

If the task asks the agent to read contents of files, e.g. it's "Write a spec based on notes in my-file.md", copy
contents of these files into TASK portion of the knowledge file. When answering the questions you'll be given just
the knowledge file, so all the relevant context needs to be included there.

## Saving the output

Prepare the file contents, once they are ready ask the user where to store it.
