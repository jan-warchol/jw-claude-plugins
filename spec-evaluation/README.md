# spec-evaluation

Skills for evaluating and comparing plans and specification documents.

## Skills

### `structural-evaluation`

Scores one or more spec files on their structural quality using a rubric. It checks five topic
areas — Goal, Requirements, Solution, Out of scope, and Uncertainty — each on a 0–3 or 0–4 point
scale (17 points total). In parallel, it runs `measure.py` (via `uv run`) to compute prose
metrics: word count, average section/paragraph/bullet length, and code snippet ratio. Outputs a
side-by-side comparison table of scores and metrics when given multiple specs.

### `technical-evaluation`

Scores one or more specs against a tiered key-points criteria file (Must / Should / Could / Should
not / Must not). Each criterion is worth a fixed number of points depending on its tier (Must = 10,
Should = 3, Could = 1, with negatives for negative tiers); Must and Should criteria also support
partial credit (half points) when a concept is only partially addressed. Produces a per-criterion
scoring table, notes on non-obvious scores, and a summary table showing positive, partial, and
negative match counts per tier plus an overall percentage score.

### `criteria-extraction`

Reads one or more plan/spec files and synthesizes them into a single tiered key-points reference
file (`key-evaluation-points.md`). The output is a rubric (Must / Should / Could mention) used as
input to `technical-evaluation`. Must Not / Should Not sections are intentionally left empty —
those require manual curation.

### `preparing-knowledge-file`

Prepares a self-contained "knowledge file" to be used during automated evaluation runs. It
anticipates the questions that the `catnip:complexity-aware-spec` skill would ask a user, collects
answers (up to 20 via `AskUserQuestion`), prepends verbatim copies of any referenced task or
extra-knowledge files, and writes everything into a structured output file. This file later drives
the simulated-user hook so eval runs can proceed without a human present.

## Hooks

### `allow-measure-script.sh` (PreToolUse on Bash)

Auto-approves any Bash command that invokes `measure.py`, so the structural evaluation skill can
run its metrics script without requiring a manual permission confirmation.

### `answer-ask-user-question-with-knowledge.sh` (PreToolUse on AskUserQuestion)

When `$CLAUDE_EVAL_SIM_USER_KNOWLEDGE_PATH` is set to a readable knowledge file (produced by
`preparing-knowledge-file`), this hook intercepts every `AskUserQuestion` call and answers it
automatically by spawning a headless `claude -p` instance that role-plays the user using the
knowledge file contents. This enables fully automated evaluation runs where no human needs to click
through questions. If the env var is unset or the file is missing, the hook disengages and the real
user is prompted normally.

### Simulated-user configuration

| Variable                          | Effect                                              |
| --------------------------------- | --------------------------------------------------- |
| `CLAUDE_EVAL_SIM_USER_KNOWLEDGE_PATH` | Path to the knowledge file (required to activate)   |
| `CLAUDE_EVAL_SIM_USER_MODEL`      | Model passed to `claude -p` (e.g. `claude-haiku-4-5`) |
| `CLAUDE_EVAL_SIM_USER_EFFORT`     | Effort level passed to `claude -p`                  |
