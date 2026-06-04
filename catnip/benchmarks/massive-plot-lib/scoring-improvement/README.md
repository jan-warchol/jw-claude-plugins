# Scoring-improvement experiment log

Goal: make `technical-evaluation` scoring **consistent** (low run-to-run variance) and
**accurate** (close to a hand-verified ground truth) — starting with a single spec.

## Target spec

`catnip-phased-tasks-e57a9ad/01/compressed.md`, scored against the **current**
`catnip/benchmarks/massive-plot-lib/tech-criteria.md` (157 max), with
`reference-spec/full-spec.md` as source of truth.

Chosen because it has the largest inter-run gap of any spec we have two baselines for
(39% in `evaluation.md` vs 62% in `detailed-tech-evaluation-breakdown.md`) and is dense
with explicit, checkable contradictions (NaN pen-lift, "no manual tuning", "Float64Array
required", IQR outlier detection, "log is a separate code path").

## Why those two baselines disagreed

1. **Criteria-version confound** — `evaluation.md` used an older criteria set (Should out
   of 16, Could out of 17 → 145 max). `detailed-…-breakdown.md` and the current file have
   19 Should / 20 Could → 157 max. Not the interesting part.
2. **Direction-of-meaning failures (the real bug)** — on identical criteria the two runs
   flip between +full / 0 / −full. Errors go in *both* directions across runs, confirming
   the `scoring-quality-findings.md` diagnosis that the evaluator scores topic *presence*,
   not *direction*.

## Ground truth (this spec)

Hand-scored total: **60 / 157 ≈ 38%** (see `ground-truth-01-compressed.md`). Note the
careful key lands near `evaluation.md` (39%) and far from the detailed breakdown (62%) —
i.e. the detailed breakdown was systematically too lenient. Ambiguous calls (where my
judgment could reasonably differ) are isolated in `ambiguities-for-review.md`.

## Methodology

- Evaluator runs are spawned as fresh-context subagents that read the live SKILL.md +
  criteria + spec and follow the skill. Edits to skill/criteria take effect immediately.
- Fixed model for ALL evaluator runs: **sonnet** (keeps before/after comparable + affordable).
- N = 3 runs per configuration. Track per-criterion mode/spread + total spread + accuracy
  vs. ground truth (mean absolute error in points; contradiction-detection recall).

## Hypothesis on the scoring mechanism (re: finer-grained partials)

The dominant variance is on the **direction** axis (agree / silent / contradict), not the
**magnitude** of partial credit. Adding more partial buckets (thirds, etc.) gives the agent
*more* freedom to disagree run-to-run and would likely hurt consistency. So the planned fix
separates two orthogonal decisions and forces the first to be written down with evidence:

1. **Stance** per criterion: AGREES / SILENT / CONTRADICTS (+ a quoted snippet or "none").
2. **Completeness** (only if AGREES): FULL or PARTIAL.

Magnitude stays coarse for now. If post-fix variance is still high *and* concentrated in
partial-credit magnitude, revisit granularity then. Logged as a suggestion either way.

## Experiment runs

See `EXPERIMENTS.md` for the full per-run detail. Headline result on `01/compressed.md`
(3 fresh sonnet runs per config):

| Config | Spread (01/compressed) | % range |
|--------|--------|---------|
| Baseline (unmodified skill) | 12 pts | 32–40% |
| After skill+criteria fixes (v4) | 3 pts | 34–36% |
| After expert feedback + M5 hardening (final) | **0 pts** | **44%** (= ground truth) |

**On the tuned spec, scoring is now essentially deterministic and on the ground truth.**
Direction-of-meaning errors (the core bug in `scoring-quality-findings.md`) are eliminated and the
fix **generalizes**: across every run on three specs, contradiction calls are unanimous within each
lineage *and* correctly flip per spec (e.g. log-as-symlog is −3 for the two specs that use a
separate log path, +3 for the one that genuinely makes log a degenerate symlog).

**Generalization caveat:** on two *unseen* specs (02, 03) within-spec spread was 17 / 10 pts
(measured before the final M5 hardening). That residual is entirely partial-credit *magnitude*
(SILENT/PARTIAL/FULL boundary calls on a handful of criteria), not direction errors. See
`EXPERIMENTS.md` Round 5–6.

**Round 8 update — 02 & 03 now have hand-verified GT keys and are re-validated.** Under the current
171-pt scheme, GT(02) = **88 / 51%**, GT(03) = **95 / 56%**; cross-spec ranking 01 (69/40%) < 02 < 03
holds. Re-running surfaced the residual magnitude wobble on ~8 criteria; 8 of those were tightened in
`tech-criteria.md` (M2 uPlot-naming, S2 dual-regime, S3 untethered-FPS, S10 optional-marker, S12
stacking, S13 framework-core ladder, C7 append-vs-streaming, C8 Float64-is-silent), and the
genuinely-debatable rest (S11 tooltip, S14 input surface, C12 nearest-point readout, C17, S7) are
logged in `ambiguities-for-review.md`. Post-edit within-spec spread: 02 = 5, 03 = 4 (down from 8/8);
the S13 direction errors are eliminated. GT keys: `ground-truth-02-compressed.md`,
`ground-truth-03-compressed.md`. **One direction miss the runs made *unanimously*** (a criterion-
wording gap, not an evaluator inconsistency): 02's incremental-append was read as a forbidden
streaming optimization (C7 −1) when it is really a full redraw (+1); the C7 wording now says so. The
edits were checked against 01's key; the M2 edit initially over-tightened and regressed 01 (caught by
a 01 re-run) and was softened — see `EXPERIMENTS.md` Round 8.

## What was changed (the fixes that worked)

**`spec-evaluation/skills/technical-evaluation/SKILL.md`** (general, low overfitting risk):
1. **Mandatory two-step scoring** — record the spec's stance (AGREES / SILENT / CONTRADICTS) with a
   quoted snippet *before* assigning a number; judge stance on the criterion's **core concept**
   (rejecting a *secondary* detail stays AGREES; rejecting the *core* is CONTRADICTS); a
   contradiction is **never** scored 0. → killed the direction errors.
2. **Single-bucket SHOULD partial** — partial = a flat 2, no 1-vs-2 judgment. → killed the
   magnitude jitter. (Evidence-backed answer to the granularity question: *coarser* is more
   consistent; finer/thirds would be worse.)

**`tech-criteria.md`** (faithful to the reference, but tuned on one spec — re-validate):
3. Inline **anti-pattern cues** ("… CONTRADICTS") on directional criteria (NaN, log-as-symlog,
   hover, symlog override, decimation, tick precision).
4. **Core-vs-secondary FULL/PARTIAL clarifications** on M2, M6, S10, S13, C1, and a **scope fix**
   on C8 (internal storage, not input type — removed a false-positive contradiction).

## Open items for the human/expert

- `ambiguities-for-review.md` lists the genuinely-debatable calls; rows tagged **[ENCODED → x]**
  are now *consistent* because the criteria steer them, but the chosen value is unconfirmed. The
  M4 log-as-symlog severity (−10 vs 0) and S8 hover (−3 vs 0) are the highest-impact open ones.
- **Validate beyond this spec:** rerun the 02 and 03 lineages (and initial/enriched phases) with
  the updated skill+criteria to check the criteria edits generalize and didn't overfit to `01`.
- Residual ±1 jitter on S12 (canvas-stacking full-vs-partial) left as-is — not worth chasing on
  a single spec.
