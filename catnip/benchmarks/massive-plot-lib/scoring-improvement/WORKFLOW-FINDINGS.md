# Workflow findings — evaluation design session

## The overall workflow (context for future agents)

The goal is to measure whether a **spec-generating skill** produces better specs than a plain agent
would on its own, and to track improvement as the skill is updated.

### Benchmark cases

Each benchmark has:
- A **prompt** describing a task for which a spec should be generated.
- Optionally, a **reference spec** — an ideal hand-crafted spec for that prompt. Some benchmarks
  also have a reverse-engineered prompt designed to reproduce the reference. The massive-plot-lib
  benchmark is an example of this kind.
- Some benchmarks have only a prompt with no reference spec.

### Spec generation (per benchmark)

For each benchmark case, two sets of specs are generated:
- **Baseline (3 runs):** spec generated without the skill, just a plain agent. Reference point for
  how well an agent performs on its own.
- **Skill-generated (3 runs):** spec generated using the current version of the spec-writing skill.

Running 3 times each captures generation variance and makes the comparison more reliable.

### Criteria file creation

To evaluate the specs, a **tech criteria file** is needed (MUST/SHOULD/COULD tiers). How it's
created depends on whether a reference spec exists:

**With a reference spec:** An agent extracts the most important design decisions from the reference
spec using the `criteria-extraction` skill, tiers them, and the result is optionally refined
manually. The reference spec is the ground truth, so the criteria directly reflect what a
"correct" spec should cover.

**Without a reference spec:** All generated specs (baseline + skill, across runs) are fed to the
`criteria-extraction` skill together. The assumption is that agents generally produce reasonable
specs and, when combined, their outputs cover most of what matters — even if each individual run
has gaps. The extracted criteria are then refined manually. This is less rigorous than having a
reference spec, but practical when one doesn't exist.

Either way, the criteria file is a **one-time artifact per benchmark domain**, not regenerated on
every evaluation run. It captures what a good spec should cover, in a form the evaluator can score.

### Evaluation and comparison

Once criteria exist, the `technical-evaluation` skill scores each spec against them and produces a
percentage (e.g. 40%, 57%). This score is the basis for comparison:
- Baseline specs vs. skill-generated specs (for the same skill version): does the skill add value?
- Old skill version vs. new skill version: does a skill change actually improve the output?

This comparison only works if the evaluation scores are **reliable** — low run-to-run variance and
accurate relative to ground truth. That's the problem that the calibration work (rounds 1–9 in
`EXPERIMENTS.md`) was solving.

### Why evaluations were unreliable (the original problem)

Two failure modes were found:

1. **Direction-of-meaning errors:** An agent would see that a spec mentioned the same keywords as
   a criterion and score it as a match — even when the spec was actually contradicting the
   criterion (e.g. the spec said "log is a separate code path", which directly contradicts the
   criterion "log is a special case of symlog"). The agent scored *topic presence*, not *stance*.

2. **Partial-credit magnitude jitter:** For criteria where a spec partially addressed the
   requirement, agents disagreed run-to-run on *how much* partial credit to award (e.g. 1 vs 2
   out of 3), causing ±10 pt swings in the total score.

Both are now fixed (see `README.md` and `EXPERIMENTS.md` for the full calibration story).

### The calibration / evaluation-tuning loop

When evaluation scores are unreliable, the fix requires:
1. Building a **hand-verified ground-truth key** for a specific spec — what each criterion's
   correct score actually is, based on careful reading of the spec against the reference.
2. Running the evaluator and comparing its output to the ground truth to find discrepancies.
3. Fixing either the **evaluation skill** (general fixes, low overfit risk) or the **criteria
   wording** (specific fixes, higher overfit risk — only encode when the reference is unambiguous).
4. Re-running to confirm the fix, then generalizing to other specs.

This is the `evaluation-tuning` skill's job, and it's expensive (see section on token burn below).

The calibration loop is **genuinely necessary** for new benchmark domains: you cannot pre-populate
"what does a contradiction look like" without seeing actual generated specs that make those design
choices. Empirical discovery is unavoidable.

However, calibration should be **faster for future benchmark domains** because the skill-mechanism
fixes from rounds 1–9 (the stance step, single-bucket partial, core-vs-secondary rule) are now
baked into SKILL.md and carry over automatically. Only the domain-specific contradiction cues and
FULL/PARTIAL boundary rules need to be re-discovered.

---

## What was done this session

- Analyzed the token burn problem in Round 9 (daily limit hit in <30 min).
- Discussed the overall workflow and where it could be simplified.
- Restructured complex criteria in `tech-criteria.md` into an explicit sub-bullet format.

---

## 1. Why Round 9 burned so many tokens

Root causes, in order of impact:

| Cause | Detail |
|-------|--------|
| "3 runs" as the default, not an escalation | Every check — including non-regression — was a 3-run block; Round 9 ran ~25 full evaluations |
| Per-edit re-runs instead of batched fixes | Each criteria change triggered a new round of 3 runs before moving to the next change |
| Full re-evaluation for non-regression | After editing M2 and S14, all 3 settled specs were re-evaluated across all 49 criteria when only 2 changed |
| Scores in context, not on disk | ~25 runs × ~50-line scores blocks held in the orchestrating agent's context, compounding cost |
| Cross-spec generalization mid-cycle | Ran 3 specs × 3 runs after each edit rather than once at the end of a stable configuration |
| Re-running settled specs unnecessarily | e57a9ad-01/02/03 were re-run for non-regression even when the relevant criteria hadn't changed |

## 2. Proposed fixes for the evaluation-tuning skill

These should be incorporated into `spec-evaluation/skills/evaluation-tuning/SKILL.md`:

- **Phase 2: batch before re-running.** Run exactly 1 evaluation. Give opus ALL discrepancies. Fix
  ALL (a) and (b) issues in one batch. Run 1 more to confirm. Don't loop per-error.
- **Phase 3: cap the rounds.** Run 3× once. If spread is still >5 pts after a second round of 3,
  log the remaining wobble as an ambiguity rather than continuing.
- **Non-regression: targeted, not full.** After a criteria edit, spawn one evaluator and ask it to
  score ONLY the modified criteria for each settled spec. Supply the criterion text inline; no need
  to re-read the whole criteria file.
- **Write scores to disk.** Evaluators write their scores block to `scores/{spec-id}-run-N.scores`.
  Orchestrator reads from files, not context.
- **Reuse before re-running.** Check EXPERIMENTS.md and the settled GT keys before spawning any
  evaluator. If a spec has a verified score for the current skill+criteria and neither has changed,
  that score is valid.
- **Cross-spec once, at the end.** 3 specs × 3 runs costs ~50–100k tokens on sonnet. Run it once
  after Phase 3 is stable on the primary spec, not after each edit.

## 3. Overall workflow — what's right and what could change

**The workflow shape is correct.** The steps (generate specs → extract criteria → evaluate →
compare) are not redundant; the flow is the right structure for longitudinal comparison across
skill versions.

**The contradiction-analysis skill is a calibration tool, not a production step.** The technical
evaluation's stance step (AGREES/SILENT/CONTRADICTS) already catches contradictions when the
criteria are clear enough. The separate contradiction-analysis skill was needed for bootstrapping
ground-truth keys; it shouldn't be a routine step once the criteria are calibrated for a domain.

**Numerical scores vs. comparative evaluation:** The current approach scores each spec
independently and compares numbers. For within-session comparisons ("is pipeline A better than
pipeline B?"), a *comparative* evaluation — feed all specs to one agent and ask for a ranking with
reasoning — is more reliable and cheaper. The tradeoff is it can't compare across time (you'd need
to re-run historically). For longitudinal tracking (is the skill improving version-over-version?),
independent numerical scores are needed.

## 4. Criteria file format — proposed change

The complex criteria in `tech-criteria.md` can be restructured from dense prose into explicit
sub-bullet format. Example:

**Before:**
```
- Input formats: number[], Float32Array, Float64Array, number[][] row-oriented; random access
  required; sorted by X assumed. The core is a flexible multi-format input surface. FULL = offers
  the full surface (number[] plus typed arrays, ideally row-oriented). Accepting several of the
  listed types but omitting one ... without rejecting any, is PARTIAL. A spec that *explicitly
  requires a single typed array and rejects number[]* ... CONTRADICTS ...
```

**After:**
```
- Input formats: number[], Float32Array, Float64Array, number[][] row-oriented; random access
  required; sorted by X assumed
  FULL: offers the full multi-format surface (number[] plus typed arrays, ideally including row-oriented)
  PARTIAL: accepts several listed types but omits one, without rejecting any
  CONTRADICTS: explicitly requires a single typed array and rejects number[] (e.g. "Float64Array required (not number[])")
```

**Labels used:** `FULL`, `PARTIAL`, `CONTRADICTS`, `SILENT` (for cases where a specific choice
should be scored as SILENT, not a contradiction), `Secondary` (for details that don't affect the
stance and should not be treated as a checklist).

**Why this helps:** The evaluator no longer has to parse scoring rules out of dense prose.
CONTRADICTS and PARTIAL rules are immediately visible. Future criteria edits are more surgical.

**For future benchmark domains:** The `criteria-extraction` skill should be updated to produce this
structured format from the start — at minimum adding a `CONTRADICTS:` sub-bullet for any criterion
where the reference spec has an explicit "do NOT do X" statement. This won't eliminate the
calibration loop (empirical contradictions are still discovered later) but will reduce its scope.
