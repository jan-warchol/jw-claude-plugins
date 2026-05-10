# Simulated User — Specification

## Overview

The Simulated User is a Claude Code subagent that acts as a synthetic test subject
during skill evaluation runs. It holds a knowledge file containing pre-defined
answers to anticipated questions, and responds only to what it is explicitly asked —
never volunteering information beyond the scope of each question. This controlled
information release is the core mechanism that enables measurement of whether the
main agent asks the right clarifying questions.

---

## Goals

- Automate the "user" role during skill evaluation without manual intervention
- Ensure the main agent only receives information it actively requests
- Produce a structured log of every question asked and answer given per test run
- Enable comparison across runs as the skill under test evolves

---

## Non-Goals

- General-purpose conversational simulation
- Multi-turn dialogue memory (each question is answered independently)
- Evaluating the quality of answers — only the questions are measured

---

## Architecture

```
  User
   │
   │  /simulate-user spec.md constraints.txt
   ▼
┌─────────────────────────────────────────┐
│         Simulation Skill                │
│  - validates file paths                 │
│  - spawns subagent with files           │
│  - injects instruction into main agent  │
└───────────────┬─────────────────────────┘
                │ activates
                ▼
┌─────────────────────────────────────────┐        ┌─────────────────────────┐
│              Main Agent                 │        │  Simulated User         │
│  (skill under test, unmodified)         │        │  Subagent               │
│                                         │        │                         │
│  asks clarifying questions ─────────────┼───────►│  reads knowledge files  │
│                                         │        │  answers only what      │
│  receives answer only       ◄───────────┼────────┤  was asked              │
│                                         │        │  logs Q&A entry         │
└─────────────────────────────────────────┘        └─────────────────────────┘
```

The main agent's system prompt instructs it to direct all clarifying questions to
the Simulated User subagent rather than the human user. The knowledge file is loaded
only into the subagent's context — the main agent never has direct access to it.

---

## Components

### 1. Knowledge File(s)

One or more free-form text files — existing feature specifications, requirement
documents, user stories, or any prose — passed in at invocation time. The subagent
reads them in full and uses LLM understanding to answer questions from their content.

No special format or structure is required. Multiple files may be provided; the
subagent treats them as a single unified knowledge base.

**Examples of valid knowledge files:**

- A markdown feature spec (`feature-auth.md`)
- A plain text requirements document (`requirements.txt`)
- A mix of both (`spec.md`, `constraints.txt`, `ux-notes.md`)

The subagent answers by extracting only the information relevant to each specific
question. If the answer to a question is not present anywhere in the files, it
returns a no-answer response (see Subagent Behaviour below).

---

### 2. Simulated User Subagent

A Claude Code subagent defined in `.claude/agents/simulated-user.md`.

**System prompt (abridged):**

```
You are a simulated user being interviewed by an AI agent that is trying to
gather requirements before starting a task.

You have access to a knowledge file that contains everything you "know".
Your behaviour rules:

1. Answer ONLY the specific question asked. Do not volunteer related information
   that was not explicitly requested.
2. Match the question to the closest topic in the knowledge file using your
   understanding of intent, not keyword matching.
3. If the question has no match in the knowledge file, respond with exactly:
   "I don't have information about that."
4. Never summarise, preview, or hint at what other information you hold.
5. Keep answers short — one to three sentences maximum.
6. After answering, append a JSON log entry to the session log file (see Logging).
```

**Permissions:**

- Read access: knowledge file, log file
- Write access: log file only
- No bash, no web fetch, no file edits outside the log

---

### 3. Simulation Skill (`simulate-user`)

A separate Claude Code skill, user-invocable only (not usable by the main agent),
that activates the simulation mode for the current session.

**Invocation:**

```
/simulate-user path/to/spec.md path/to/constraints.txt ...
```

One or more knowledge file paths are passed as arguments. The skill:

1. Reads and validates that all provided paths exist and are readable
2. Spawns the Simulated User subagent, passing the file paths into its context
3. Injects an instruction into the main agent's context via a `UserPromptSubmit`
   hook (or equivalent) telling it to direct all clarifying questions to the
   subagent rather than the human user
4. Records the `run_id` and the list of knowledge files in the session log header

The skill is intentionally separate from the skill under test. This means:

- The skill under test requires no modification to support simulation mode
- Real-user and simulated-user modes are toggled purely by whether
  `/simulate-user` is invoked at the start of the session
- The simulation infrastructure is reusable across any skill being evaluated

**Skill definition location:** `.claude/skills/simulate-user.md`

**Allowed callers:** user only (not agent-invocable)

---

### 4. Q&A Log

The subagent appends a structured entry to a log file after each answer.

**Format:**

```json
[
  {
    "run_id": "2024-03-15T10:42:00Z",
    "knowledge_files": ["spec.md", "constraints.txt"],
    "question_raw": "What platform should the app target?",
    "answer_given": "Web, desktop browsers only, no mobile required.",
    "answered": true,
    "source_file": "spec.md"
  },
  {
    "run_id": "2024-03-15T10:42:00Z",
    "knowledge_files": ["spec.md", "constraints.txt"],
    "question_raw": "Do you have a preferred colour scheme?",
    "answer_given": "I don't have information about that.",
    "answered": false,
    "source_file": null
  }
]
```

`run_id` is a timestamp or UUID shared across all entries from a single evaluation
run, so multiple runs can coexist in the same log file. `source_file` records which
knowledge file the answer was drawn from, which is useful when multiple files are
provided.

---

## Evaluation Workflow

1. Select one or more knowledge files for the scenario (existing specs, requirement
   docs, etc. — no reformatting needed)
2. Start a Claude Code session with the skill under test active
3. Invoke `/simulate-user path/to/file1.md path/to/file2.txt ...`
4. Give the main agent its task prompt as normal
5. The main agent runs, directing clarifying questions to the subagent
6. At session end, inspect the Q&A log:
   - **Questions asked**: what the main agent chose to ask
   - **Questions not asked**: information present in the knowledge files that was
     never surfaced
   - **Unanswerable questions**: entries where `answered: false` (question outside
     the knowledge files)
7. Compare across runs as the skill under test evolves

---

## Leakage Risk and Mitigations

The main risk is the subagent returning more information than the question warrants,
which would give the main agent knowledge it did not earn.

| Risk | Mitigation |
|---|---|
| Subagent volunteers extra context | Strict system prompt rule 1 + 4; short answer constraint |
| Main agent reads knowledge files directly | Subagent-only read permission on knowledge file paths (via `PreToolUse` hook on `Read`, checking `agent_type`) |
| Subagent leaks scope via "I can't answer X, Y, Z" | Rule 4: no hints or previews of held knowledge |
| Large knowledge file summarised into subagent response | Short answer constraint (1–3 sentences); subagent extracts only the relevant fragment |
| Main agent infers topics from answer phrasing | Out of scope — acceptable residual risk |

The `PreToolUse` hook restriction on the knowledge file path is optional but
recommended for rigorous evaluations. It requires a hook script that checks
`agent_type` against the file path and denies reads from the main agent context
(see prior discussion on per-agent file ACLs).

---

## Open Questions

- **No-answer behaviour**: Should the subagent return a fixed sentinel string or
  natural-language "I don't have information about that"? A fixed sentinel makes
  log parsing easier; natural language is more realistic for the main agent.
- **Multi-question `AskUserQuestion` calls**: The tool supports asking several
  questions at once. The subagent should answer each independently and log each
  as a separate entry — but the spec does not yet define how it handles partial
  matches (some questions answerable, some not) within a single call.
- **Knowledge file path handling**: Should paths be relative to the project root,
  the current working directory, or absolute only? Relative-to-project-root is
  probably the least surprising default.
- **Subagent context limits**: Very large knowledge files (e.g. a long spec) may
  approach context limits when combined with conversation history. A chunking or
  summarisation strategy may be needed for large inputs.
- **Coverage scoring**: The spec describes the raw log but not an automated scorer.
  A separate eval script consuming the log is a natural next step, potentially
  producing a coverage percentage against the knowledge file content.