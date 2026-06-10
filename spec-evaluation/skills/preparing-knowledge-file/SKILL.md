---
name: preparing-knowledge-file
description: Prepare knowledge file that will be used for planner evaluation
disable-model-invocation: true
---

### Usage

```
/preparing-knowledge-file The task to prepare promp text (complexity: <score>) [Extra knowledge: /some/path [/more/paths ...]] [Output path: /some/other/path]
```

`[` and `]` indicate optional parts.

## Skill inputs

This skill requires a prompt for plan/specification (the same thing that would be passed to
catnip:complexity-aware-spec skill) and its complexity rating on a 1-10 scale. If not given both as
skill arguments, immediately ask user for the missing pieces.

It can also get extra paths to files with more knowledge that catnip:complexity-aware-spec wouldn't
get. These will be passed after the complexity score and are not part of the prompt.

## Task to perform

You need to prepare to answer questions that an agent running catnip:complexity-aware-spec would ask
the user with AskUserQuestion tool. Your task right now is to prepare for all questions that such
agent would plausibly ask and write down the answers.

For all questions that are important and aren't answered by context files, you must ask user for the
answer. For other questions that don't have clear answers, you'll be able to pick or invent your own
answers.

## Two categories of files

Two kinds of files may end up referenced while preparing the knowledge file. Keep them distinct —
they differ in what catnip:complexity-aware-spec will see:

- **Task-prompt files** — files the prompt itself points the agent to read (e.g. "Write a spec based
  on notes in my-file.md"). When catnip:complexity-aware-spec is later run with this prompt, it will
  follow those references. Their contents ARE part of its input.
- **Extra knowledge files** — file paths passed to preparing-knowledge-file after the complexity
  score. catnip:complexity-aware-spec will NOT see these; they exist purely so
  preparing-knowledge-file can resolve non-ambiguous answers without bothering the user.

Both kinds MUST be embedded verbatim in the output knowledge file, each in its own section (see the
template below). Embedding makes the knowledge file self-contained: any downstream consumer
evaluates against the same context the answers were prepared against, even if the source files later
change or move.

When thinking about what questions catnip:complexity-aware-spec may answer, remember that
catnip:complexity-aware-spec only sees the prompt and the task-prompt files. Anything resolvable
only from the extra knowledge files is not "obvious from the prompt" from its perspective.

## Questioning the user

Prepare up to 20 most important questions that don't have clear answer in the existing knowledge and
query the user with AskUserQuestion tool. Write the questions and answers verbatim into the USER
ANSWERS section. If the user interrupts in order to write a free-form answer, take this answer and
then get back to using AskUserQuestion tool.

## Preparing more answers

The idea is that you'll be able to answer any sensible question consistently, based just on this
written-down knowledge.

For any question you think the agent running catnip:complexity-aware-spec is likely to ask and that
wasn't answered by the user or is not unambiguously answered by the extra context, write down the
answer in PREPARED ANSWERS section. Make it succinct — long enough to resolve ambiguities
consistently. Whether you write it down in Q&A format or just as a list of decisions is up to you,
as long as you'll be able to understand it without ambiguity.

The answers must not contradict any of the given knowledge and context.

## Preparing the output

The output file has the following sections, in order. Omit `TASK FILES` and/or `EXTRA KNOWLEDGE`
entirely if no files of that kind were involved.

```
=== TASK (complexity <complexity score given>) ===
<the initial prompt from the user, verbatim. Strip out any "extra knowledge:
<path>" pointers that were addressed to preparing-knowledge-file itself —
those aren't part of what catnip:complexity-aware-spec would receive.>
=== TASK ===

=== TASK FILES ===
Files referenced directly by the prompt. Agent asking you question should have access to them.

--- FILE: <path as it appeared in the prompt> ---
<file contents, verbatim>
--- END FILE ---

--- FILE: <another path> ---
<file contents, verbatim>
--- END FILE ---
=== TASK FILES ===

=== EXTRA KNOWLEDGE ===
This extra knowledge is known to you, but the agent asking you questions is not aware of this.

--- FILE: <path> ---
<file contents, verbatim>
--- END FILE ---
=== EXTRA KNOWLEDGE ===

=== USER ANSWERS ===
These questions were answered directly by a human user.

<Q&A list with questions and answers given by user directly>
=== USER ANSWERS ===

=== PREPARED ANSWERS ===
These answers were prepared by AI agent in order to reduce ambiguity.

<Q&A list with questions and answers prepared by you>
=== PREPARED ANSWERS ===
```

TASK FILES and EXTRA KNOWLEDGE sections can be skipped entirely if there are no relevant files to
include in them.

Always embed file contents verbatim, never just a path reference. Even if the files are large,
include them fully.

## Saving the output

Once you are ready, write the output to given file path.

If not given output path, save the result to a file in /tmp/ with some unique name, and afterwards
ask if it should be moved to another place.
