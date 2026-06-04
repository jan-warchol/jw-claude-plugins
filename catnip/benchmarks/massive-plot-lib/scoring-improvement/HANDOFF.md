# Handoff

## ✅ Round 9 done (this session) — cross-pipeline generalization (manual-5d0e14e + cc-base)

Ran the validated skill + `tech-criteria.md` against the two *other* generation pipelines (3 sonnet
runs per spec file; all totals recomputed by hand from the `scores` blocks). See `EXPERIMENTS.md`
Round 9 for full detail. Headlines:

1. **Pipeline structure was different than the HANDOFF assumed**: `manual-5d0e14e/{01,02,03}` and
   `cc-base/spec-{1,2,3}` are each **3 independent runs of one prompt**, not 3 distinct specs — so all
   9 specs across the 3 pipelines target the *same* reference. Within-family spread = generation
   consistency; cross-family = pipeline quality. (Scored the `compressed-1500w` of the manual family.)
2. **Criteria generalize well.** Direction-of-meaning is solid and several cues never exercised by the
   `e57a9ad` family fired **correctly and unanimously**: M5 pixel-coord Path2D = −10 (cc-base spec-2),
   S20 separate-log-path = −4 (cc-base spec-3), S17 built-in decimation = −4 (manual-03), **SN2
   bundle-size target = −4 (cc-base spec-3, first time ever triggered)**. Cross-pipeline scores all
   land 40–57%, discriminating real per-generation design divergence.
3. **Two wording problems found and fixed (both non-regressing):**
   - **M6 (stable-series-ids, MUST):** manual-01's terse "invalidated only on … add/remove" caused a
     ±10 direction split (−10/−10/+10) — the whole source of its 19-pt spread. Clarified M6 so keying
     on stable IDs = FULL; listing invalidation triggers still AGREES; CONTRADICTS only for unstable
     keys / full-cache-flush. → manual-01 spread **19→2**, M6 now +10/+10/+10.
   - **S14 (input formats):** encoded a FULL/PARTIAL/CONTRADICTS ladder — explicit "Float64Array
     required (not number[])" = −4 (matches e57a9ad-01 key); accept-several-omit-one = +2.
   - **Non-regression confirmed:** e57a9ad-01 = 69/69 (exact), -02 = 88 (exact), -03 = 97 (within its
     normal 95–98 band). manual-01 post-fix = 92/93/91.
4. **Left OPEN for the expert** (logged in `ambiguities-for-review.md`): S11 tooltip anchor+callback
   FULL-vs-PARTIAL (cc-base spec-3), C17 out-of-scope-vs-planned (manual-03, recurs), S8 autofit-Y
   "never widen" secondary (minor).

### ▶ Next session options
- **Get the expert's calls** on the OPEN items above + the still-open round-8 ones (S11, C12, M4
  severity, S8 hover) — they're the only remaining wobble; forcing them further risks overfitting.
- Optionally score the manual family's **`compressed-1000w`** variants (compression-budget vs fidelity
  datapoint) and/or the `enriched.md` phases — same protocol; non-regression guard against 69/88/95.
- Build hand-verified GT keys for the new pipeline specs only if accuracy (not just consistency) is
  needed — Round 9 measured consistency + did targeted non-regression, not full GT keys for the 6 new
  files.

---

## ✅ Round 8 done — 02 & 03 validated, magnitude wobble pinned

All three tasks below are complete. Summary (see `EXPERIMENTS.md` Round 8 for detail):

1. **Re-ran 02 & 03** (3 sonnet runs each) under current skill+criteria: within-spec spread 8 / 8
   (down from the stale 17 / 10). Direction-of-meaning unanimous + correct in every run.
2. **Built hand-verified GT keys**: `ground-truth-02-compressed.md` (**88 / 51%**),
   `ground-truth-03-compressed.md` (**95 / 56%**). Cross-spec ranking 01 (69/40%) < 02 < 03 holds.
3. **Pinned the magnitude wobble** to ~8 criteria. Tightened 8 in `tech-criteria.md`
   (M2 uPlot-naming, S2 dual-regime, S3 untethered-FPS, S10 optional-marker, S12 stacking,
   S13 framework-core ladder, C7 append-vs-streaming, C8 Float64-is-silent); logged 5 debatable ones
   (S11, S14, C12, C17, S7) in `ambiguities-for-review.md`. Confirmation re-runs: **02 spread 8→5,
   03 spread 8→4**, both centered on their GT keys; S13 `−4` direction errors eliminated. Every edit
   was validated to leave 01's settled GT of 69 untouched (one over-tighten on M2 was caught by a 01
   re-run and reverted; 01 re-confirmed deterministic at 69/69/69).

### Open for the expert (next): the 5 logged ambiguities in `ambiguities-for-review.md` under
"New calls surfaced on specs 02 & 03 (Round 8)" — S11 tooltip (hedged = PARTIAL?), S14 typed-array
input surface, C12 nearest-point readout (CONTRADICTS vs SILENT), C17 out-of-scope vs planned, and
the M2-03 decimation-fairness read (PARTIAL vs FULL). Genuine judgment calls; encode in the criteria
only where the reference is unambiguous, else leave as logged.

---

## ✅ (DONE in Round 9 — see top) — evaluate the other two pipeline families

So far everything has been scored on the `catnip-phased-tasks-e57a9ad/` family (specs 01/02/03,
single `compressed.md` each). Next: run the **same** validated skill + `tech-criteria.md` against two
*other* generation pipelines for the same underlying three specs, to (a) further test that the
Round-8 criteria generalize beyond the family they were tuned on, and (b) compare pipelines.

### The two directories and their layout

1. **`catnip-phased-manual-5d0e14e/{01,02,03}/`** — a *manual* phased pipeline. Each spec dir has
   `initial.md`, `enriched.md`, **`compressed-1000w.md`**, **`compressed-1500w.md`** (two compressed
   word-budgets, NOT a single `compressed.md`), plus a per-spec `evaluation-report.md` and `README.md`.
   - Decide which variant(s) to score. Recommended: the **`compressed-1500w.md`** of each (closest in
     length/role to the `e57a9ad` `compressed.md` we've been scoring), and optionally `1000w` to see
     how compression budget affects fidelity. `enriched.md` is much longer (~440 lines) — score only
     if you want a length-vs-fidelity datapoint.
2. **`cc-base/`** — a flat "Claude-Code-base" pipeline: `spec-1.md`, `spec-2.md`, `spec-3.md`
   (standalone, larger: ~525–681 lines), plus `evaluation-report.md` and `contradictions.md`.
   - Confirm the spec-N ↔ 01/02/03 correspondence before comparing (read the objectives; spec-1 likely
     = 01, etc., but verify — don't assume).

### Method (reuse Round 8 exactly)

- Spawn fresh `general-purpose` subagents, **model sonnet**, **3 runs per spec file**, the prompt
  template from the original brief below (give absolute paths; ask for the summary table + a
  ```scores``` block only).
- **Recompute every total yourself from the `scores` block** — the sonnet runs frequently slip on the
  final arithmetic (this round one run reported 90 when its own scores summed to 98). Trust the
  per-criterion lines, not the run's stated total.
- Measure within-spec spread (3 runs) and, if you want accuracy not just consistency, **build a
  hand-verified GT key** per spec like `ground-truth-0{2,3}-compressed.md`.

### What to watch for

- **Pre-existing `evaluation-report.md` / `contradictions.md`** in these dirs were written under an
  *older* criteria version — do NOT treat them as ground truth or assume they match the current 171-pt
  scheme. Cross-reference only.
- **Criteria not yet exercised**: the `e57a9ad` specs happened not to stress some criteria (e.g. time
  scales, date inputs, drawing order, visual-regression testing, CSS-variable styling, robustness
  contract). A different pipeline may address these, surfacing new SILENT/PARTIAL/FULL boundary calls.
  Tighten wording only where the reference spec is unambiguous; otherwise log in
  `ambiguities-for-review.md`. **Don't overfit** (Round 3 whack-a-mole lesson).
- **Non-regression guard**: any `tech-criteria.md` edit must be checked against the three settled keys
  — `ground-truth-01-compressed.md` (69), `-02-` (88), `-03-` (95) — and ideally a quick 1–3 run
  re-confirm, exactly as the M2 over-tighten was caught and reverted this round.
- Append results as **Round 9** in `EXPERIMENTS.md`; keep the cross-pipeline comparison (does the same
  underlying spec land at a similar score across `e57a9ad` / `manual` / `cc-base`? large divergence =
  a real pipeline-quality difference; small = the criteria are pipeline-robust).

---

## (original task brief — now completed)

## The task

The technical-evaluation skill + `tech-criteria.md` have been tuned for **consistency** and are now
deterministic on the one spec they were tuned against (`01/compressed`, 3/3 identical runs). The job
for this session:

1. **Re-run `02/compressed` and `03/compressed`** (3 fresh runs each) under the *current* skill +
   criteria, and measure within-spec spread. Earlier 02/03 runs were done before two changes that
   should tighten them (the M5/M6 Path2D hardening and the SHOULD 3→4 scheme), so they need redoing.
2. **Build hand-verified ground-truth keys** for 02/compressed and 03/compressed (like
   `ground-truth-01-compressed.md`), so accuracy — not just consistency — can be measured on them.
3. **Pin down the remaining magnitude wobble.** From the last cross-spec run, residual within-spec
   disagreement was concentrated in a few SHOULD/PARTIAL boundary calls (see "Known wobble" below).
   Use the new GT keys + run disagreements to tighten the criterion wording for those — but **do not
   overfit**: only change wording where the reference spec (`reference-spec/full-spec.md`) is
   unambiguous; otherwise log it in `ambiguities-for-review.md` for the expert.

Keep it consistency-first. Direction-of-meaning is already solved and generalizes; the open work is
purely partial-credit *magnitude* on unseen specs.

## Current state (what's already done)

- **Scoring scheme** (in `SKILL.md`): MUST 10 / SHOULD 4 / COULD 1; partial = exactly half
  (MUST 5, SHOULD 2, COULD none); contradiction = negative full; should-not −4, must-not −10.
  Single partial value per tier — no finer gradation. Max for this criteria set = **171**
  (MUST 7×10 + SHOULD 20×4 + COULD 21×1).
- **Skill mechanism**: mandatory two-step scoring — record stance (AGREES / SILENT / CONTRADICTS)
  with a quoted snippet *before* scoring; judge on the criterion's **core concept** (rejecting a
  *secondary* detail stays AGREES; rejecting the *core* is CONTRADICTS); contradiction is never 0;
  Could is full-or-nothing but "full" = core covered (don't require every bundled sub-feature).
- **Criteria** (`tech-criteria.md`): MUST 7 / SHOULD 20 / COULD 21 / SHOULD-NOT 2. Has inline
  anti-pattern cues ("… CONTRADICTS") on directional criteria, FULL/PARTIAL clarifications on the
  ambiguous ones, a three-case Path2D rule, and the symlog criterion split into two SHOULDs.
- **Validated**: `01/compressed` = **69/171 = 40%**, 3/3 identical runs. This is the settled GT.

## Files

- Skill: `spec-evaluation/skills/technical-evaluation/SKILL.md` (symlinked into the plugin; edits
  take effect immediately for fresh subagents)
- Criteria: `catnip/benchmarks/massive-plot-lib/tech-criteria.md`  (current, max 171)
- Old criteria backup: `catnip/benchmarks/massive-plot-lib/tech-criteria-old.md` (reference only)
- Reference spec (source of truth): `catnip/benchmarks/massive-plot-lib/reference-spec/full-spec.md`
- Specs to evaluate:
  - `catnip/benchmarks/massive-plot-lib/catnip-phased-tasks-e57a9ad/02/compressed.md`
  - `catnip/benchmarks/massive-plot-lib/catnip-phased-tasks-e57a9ad/03/compressed.md`
  - (also available per lineage: `initial.md`, `enriched.md`; and a separate
    `catnip-phased-manual-5d0e14e/` family with initial/enriched only — extra specs if useful)
- Work log / artifacts (read these first): `scoring-improvement/README.md`,
  `scoring-improvement/EXPERIMENTS.md`, `scoring-improvement/ground-truth-01-compressed.md`,
  `scoring-improvement/ambiguities-for-review.md`

## How to run an evaluator (worked well this session)

Spawn fresh `general-purpose` subagents, model **sonnet** (fix the model so runs are comparable and
cheap), **3 runs per spec**. Give absolute paths and ask for trimmed output. Prompt template:

> Perform a technical-evaluation of ONE spec file with a fresh perspective. Do not look for prior results.
> 1. Read skill: <abs path to SKILL.md>
> 2. Read criteria: <abs path to tech-criteria.md>
> 3. Read spec: <abs path to the spec>
> 4. Follow SKILL.md EXACTLY, including the mandatory stance-recording step, scoring every criterion.
>    Use the tier point values exactly as defined in SKILL.md.
> Output ONLY: (a) the summary table (per-tier counts, total, max, percentage); (b) a ```scores```
> fenced block, one line per criterion as `TIER|short-criterion|stance|score`, every criterion included.
> Do not edit files. Do not evaluate any other spec.

Run the 3 (or 6) in parallel in one turn. To measure: collect the `scores` blocks, compute per-spec
total spread and per-criterion disagreement; compare totals to the GT key you build.

## Prior 02/03 numbers — STALE, for reference only

Measured under the OLD scheme (max 151) and BEFORE the M5/M6 Path2D hardening, so expect different
(tighter) numbers now:
- 02/compressed: 80 / 86 / 69 (spread 17, max 151)
- 03/compressed: 88 / 91 / 98 (spread 10, max 151)
Direction calls were already unanimous within each lineage and correct (02 has no outlier detection
and a separate log path; 03 genuinely implements log = symlog and has σ-based outlier detection →
SHOULD-NOT −4). Cross-spec ranking 01 < 02 < 03 is expected and sensible.

## Known wobble to target (the actual open problem)

These criteria caused most of the within-spec magnitude spread on unseen specs. For each, decide
from the reference spec whether to tighten the criterion or log as ambiguous:
- **M2 — Performance ≥ uPlot**: runs split 0 / +5 / +10. Partly a factual read ("is uPlot named in
  *this* spec at all?" → SILENT vs PARTIAL) and partly the decimation-fairness FULL bar. Check the
  02/03 spec text for whether uPlot is named.
- **S2 — Main benchmark configs**: +4 / +2 / 0 depending on whether both series×point configs are
  stated. Decide if one config = PARTIAL is the rule.
- **Tooltip (03)**: +2 vs +4 (03 hedges "nearest-point readout assumed in scope").
- **M5/M6 Path2D**: now hardened to a three-case rule (normalization absent = PARTIAL +5, never
  negative); confirm the −10 misread does not recur on 02 (02 also uses plain data coords).
- **S12 canvas-stacking**: the one accepted residual — runs read it FULL on 01; watch it on 02/03.

## Guardrails

- Edits to `SKILL.md` are general (low overfit risk). Edits to `tech-criteria.md` risk overfitting
  to whichever spec you're looking at — only encode a resolution when the reference spec is clearly
  on one side; otherwise add it to `ambiguities-for-review.md` with an `[ENCODED → x]`-style note.
- Append results to `EXPERIMENTS.md` (continue the "Round N" numbering — last was Round 7).
- Don't re-litigate direction-of-meaning; it's solved. Focus on SILENT/PARTIAL/FULL boundaries.
- Expert (Jan's friend) review notes live inline in `ambiguities-for-review.md`; the expert's
  decisions from last round are already incorporated (log demoted to SHOULD, symlog split, hover
  demoted to COULD, FPS partial-credits ms targets, "substantial address → credit" for Could).
