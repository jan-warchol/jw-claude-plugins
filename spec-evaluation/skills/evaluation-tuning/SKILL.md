---
name: evaluation-tuning
description:
  Improve a criteria-based spec evaluation (e.g. the technical-evaluation skill) so its scores are
  accurate and consistent run-to-run. Escalates from cheap single-run error-fixing to multi-run
  consistency checks. TRIGGER when the user wants to make an evaluation/scoring more reliable,
  reduce run-to-run variance, fix mis-scored criteria, calibrate a criteria file, or "tune/improve
  the evals". Not for performing an evaluation itself — use technical-evaluation for that.
---

You are improving an **evaluation mechanism** (a scoring skill + a tiered criteria file), not a
spec. The goal is scores that are both **accurate** (match a source-of-truth reading) and
**consistent** (a fresh agent re-scoring the same spec lands on the same numbers). Work in
escalating phases — cheap and shallow first, thorough only once the cheap wins are banked.

## Inputs (ask once if missing, then proceed)

- The **scoring skill** being tuned (e.g. `technical-evaluation/SKILL.md`).
- The **criteria file** (tiered Must/Should/Could/…).
- One or more **candidate specs** to score.
- The **reference spec** — the source of truth the criteria are derived from. Essential; without it
  you cannot judge accuracy. If there isn't one, say so and fall back to consistency-only tuning.

Edits to the skill/criteria must be saved to the live files so freshly-spawned subagents pick them
up immediately.

## Model assignments (mandatory)

| Role | Model | Why |
| ---- | ----- | --- |
| Find contradictions between a candidate spec and the **reference spec** | **opus** | hardest judgment; anchors ground truth |
| Judge an evaluator's output ("evaluate the evaluation") | **opus** | must catch the evaluator's own mistakes |
| The evaluator under test (runs the scoring skill) | **sonnet** (the production model) — keep it **fixed** across all runs in a comparison | this is the thing being measured |
| Stretch-goal cheap-model check | **haiku** | see Phase 4 |

Never use the same single run to both produce and bless a score. The producing model (sonnet) and
the judging model (opus) must be separate calls.

## Method — escalating phases

Pick ONE target spec to start: the one with the most room for improvement (largest known run-to-run
disagreement, or the most reference-contradicting content). Do all phases on it before generalizing.

### Phase 1 — Anchor ground truth (opus contradiction pass)

Spawn an **opus** subagent to run the sibling **`contradiction-analysis`** skill on the candidate
spec against the reference spec — that skill already finds where a candidate conflicts with the
reference, split into direct contradictions vs. weaker divergences/gaps. Opus is mandatory here.

Then (same opus agent, or a follow-up) turn that into a per-criterion **ground-truth key**: for each
criterion, the candidate's true stance vs. the reference — AGREES / SILENT / CONTRADICTS — with a
quoted snippet and the score that stance should earn. Save it as `ground-truth-<spec>.md`. Flag any
criterion whose wording is unclear or whose correct score is genuinely debatable (→ Ambiguities).

This key is the accuracy yardstick for everything that follows.

### Phase 2 — One run, fix the biggest errors

1. Run the evaluator **once** (sonnet) via the template below.
2. Spawn an **opus** judge: compare the run's per-criterion scores to the ground-truth key. Return
   the discrepancies **ranked by point impact**, each classified as one of:
   - **(a) evaluator mistake** the skill instructions should have prevented → fix the skill,
   - **(b) criterion-wording problem** (the criterion invited the mistake) → fix the criterion,
   - **(c) genuine ambiguity** (reasonable people disagree) → batch for the user, don't "fix".
3. Fix the biggest (a) and (b) issues. **Prefer general skill edits over per-criterion criteria
   edits** — skill changes generalize, criteria edits overfit to this spec.
4. **Direction errors outrank magnitude errors.** A contradiction scored as positive or absent (or
   vice-versa) is the highest-impact, highest-leverage bug — fix those first; worry about
   partial-credit size later.
5. Re-run once and confirm the big error is gone. Loop until no large single-criterion errors remain.

### Phase 3 — Consistency (3 runs)

Only once the obvious accuracy errors are fixed:

1. Run the evaluator **3 times**, fresh context, **same model**, via parallel subagents.
2. Compute the **total-score spread** and flag every criterion whose score **disagrees across the
   three runs**.
3. For each disagreeing criterion, decide with the opus judge whether the disagreement is direction
   (agree/silent/contradict) or magnitude (how much partial credit). Direction splits → tighten the
   stance rules / add an anti-pattern cue. Magnitude splits → prefer a **structural** fix that
   removes the degree of freedom (e.g. collapse partial credit to a single value per tier) over
   case-by-case wording; finer gradations make consistency *worse*, not better.
4. Re-run 3× after each change. Repeat until spread is small and stable.
5. **Have opus confirm the converged values are also _correct_** — consistency must not mask a
   stable-but-wrong answer. If a criterion is now consistent only because everyone makes the same
   defensible-but-uncertain call, that's an ambiguity for the user, not a win.

### Phase 4 — Cheap-model check (stretch)

With the evaluation now stable on sonnet, run the same 3× protocol with a **haiku** evaluator.
Report how much accuracy/consistency degrades vs. sonnet (per-tier and total). This tells the user
whether the evaluation can be run cheaply or needs the stronger model. Do not tune *for* haiku
unless asked — just measure.

### Generalize last

Everything above is tuned on one spec. Before trusting the changes, re-run Phase 3 on **2+ specs
you did not tune against**. Skill-level fixes should hold; criteria-wording fixes are where
overfitting shows up. Build ground-truth keys for those specs too if you need accuracy numbers.

## Ambiguities — collect, then present in bulk

Throughout, accumulate genuinely-ambiguous cases (unclear criterion wording; correct score
debatable; "core vs. secondary" calls) into a single `ambiguities-for-review.md`, each with: the
criterion, the range of defensible scores, and which interpretation you provisionally used.

**Do not interrupt the user per-item.** At each phase boundary, present the accumulated batch at
once: use `AskUserQuestion` for the few highest-impact decisions (it caps at 4), and point the user
to the file for the rest. When you encode a provisional resolution to keep things consistent, mark
it clearly as provisional so the user can overturn it. Consistency achieved by *picking* a
resolution is not the same as proving it correct — keep the distinction visible.

## Running an evaluator subagent (template)

Spawn `general-purpose`, model as assigned, **3 runs in parallel** when checking consistency. Give
absolute paths and ask for trimmed, machine-readable output:

> Perform a technical-evaluation of ONE spec with a fresh perspective; do not look for prior results.
> 1. Read the skill: `<abs path to scoring SKILL.md>`
> 2. Read the criteria: `<abs path to criteria file>`
> 3. Read the spec: `<abs path to candidate spec>`
> 4. Follow the skill EXACTLY (including its stance step); score every criterion; use the tier point
>    values exactly as defined in the skill.
> Output ONLY: (a) the summary table (per-tier counts, total, max, percentage); (b) a ```scores```
> fenced block, one line per criterion as `TIER|short-criterion|stance|score`, all criteria included.
> Do not edit files. Do not evaluate any other spec.

Collect the `scores` blocks to diff runs against each other and against the ground-truth key.

## Guardrails

- Fix the **skill** (general) before the **criteria** (overfit-prone). Log which you changed and why.
- Keep the evaluator model **fixed** within any before/after comparison.
- Never let a single run grade itself; opus judges, sonnet produces.
- Don't re-litigate solved layers. Once direction-of-meaning is consistent, stay on magnitude.
- Append every round to an experiments log (spec, model, the 3 totals, spread, what changed, why).

## Deliverables

- Updated scoring skill and/or criteria file.
- `ground-truth-<spec>.md` per spec you measured accuracy on.
- `ambiguities-for-review.md` — the batched open questions for the user.
- An experiments log with the per-round numbers and the rationale for each change.
