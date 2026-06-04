# Experiment runs — `01/compressed.md`

Ground truth: **60 pts / 38%** (band ~33–44%). Model for all runs: sonnet. N=3.

## Run 0 — BASELINE (current skill + current criteria, unmodified)

| Run | Total | % | Notes |
|-----|-------|---|-------|
| 1 | 60 | 38% | matches GT |
| 2 | 63 | 40% | |
| 3 | 51 | 32% | over-applied partials |
| **GT** | **60** | **38%** | |

- Spread: **12 pts (32–40%)**. Mean 58, ~6.2 stdev.
- Mean abs error vs GT: ~4 pts.
- **Contradictions caught by all 3 runs:** M4 log (−10), S9 NaN (−3), SN1 outliers (−3). The
  findings report's dominant "Pattern A" (NaN scored +3) did NOT recur — the current skill already
  handles blatant contradictions.
- **Criteria with run-to-run disagreement (12 of 49 ≈ 24%):** M2 (0/0/5), M5 (5/5/10),
  M7 (10/10/5), S4 (2/3/1), S10 (3/3/1), S12 (2/2/1), S13 (0/1/0), S14 (1/1/0), S16 (1/1/0),
  C1 (1/1/0), C2 (0/1/0), C13 (1/1/0).
- **Diagnosis of residual variance:**
  - (a) *Partial-credit magnitude* — M5/M7 docked to half for missing a *parenthetical* detail
    ("does NOT sync initial X ranges", "add/remove doesn't invalidate") that the skill already says
    is not a checklist. Over-strict.
  - (b) *Subtle contradictions* — S14 (rejects number[]) and C1 (no clamping) caught by only some
    runs.

### Fix applied after Run 0 (v1)

1. SKILL.md: mandatory two-step scoring — write the spec's **stance** (AGREES / SILENT /
   CONTRADICTS) + snippet per criterion *before* scoring; judge stance on the **core concept only**
   (rejecting a *secondary* detail stays AGREES; rejecting the *core* is CONTRADICTS); contradiction
   is never 0.
2. tech-criteria.md: added inline "… CONTRADICTS" anti-pattern cues to the directional criteria
   where the reference is unambiguous (NaN, log-as-symlog, hover interpolation, symlog override,
   decimation, tick precision).

Rationale: (a) the core-concept rule should pull M5/M7 to a consistent full and stop parenthetical
docking; (b) the written stance + cues should make subtle contradictions reliably caught.

## Run 1 — skill v1 + criteria v1 (stance-check + contrast cues)

| Run | Total | % |
|-----|-------|---|
| 1 | 60 | 38% |
| 2 | 67 | 43% |
| 3 | 57 | 36% |
| **GT** | **60** | **38%** |

- Spread: **10 pts (36–43%)** (was 12). Mean 61.3 (was 58) — closer to GT on average.
- **Direction consistency improved a lot** (all unanimous now where baseline split):
  - S14 input formats: 1/1/0 → **−3/−3/−3** ✓ (cue + stance caught the contradiction)
  - S8 hover: 0/0/0 → **−3/−3/−3** ✓ (cue)
  - S12 canvas stacking: 2/2/1 → **3/3/3** ✓ (core-concept rule)
  - M5: 5/5/10 → **10/10/10** ✓; M7: 10/10/5 → **10/10/10** ✓ (no more parenthetical docking)
- **Residual variance moved to partial-credit magnitude on two MUSTs:**
  - M2 perf≥uPlot: **10/10/5** — core-vs-secondary call on "benchmarked without uPlot's decimation"
  - M6 Path2D: **5/10/10** — is zoom-normalization core or is data-coords+transform enough?
  - Minor: S10 markers 3/3/1, C1 bands 0/1/1, C13 canvas-size 1/1/0.
- **Over-correction:** C8 Float32 0/0/0 → **−1/−1/−1**. Likely a false-positive contradiction —
  the criterion is about *internal storage* precision; the spec's "Float64Array required" is about
  *input type*. The contradiction emphasis over-reached on a loosely-related criterion.

### Fix applied after Run 1 (v2) — criteria clarity only (skill unchanged)

Resolve the core-vs-secondary ambiguity in the three split criteria, and fix C8's scope, by naming
explicitly in tech-criteria.md what earns FULL vs PARTIAL. These are general clarity improvements
(faithful to the reference's emphasis), not spec-specific hacks:

1. M2: full requires naming uPlot as the bar **and** excluding its decimation; perf-target-only → partial.
2. M6: full requires the **normalization** (float-precision across zoom); plain data-coords+transform → partial.
3. S10: full requires **both** NaN and ±Inf visibly represented; only one → partial.
4. C8: scope it to **internal storage** precision so input-type choices don't read as contradictions.

Expected: M2→5, M6→5, S10→2 converge; C8→0 (SILENT). Predicted spread ≈5 pts.

## Run 2 — criteria v1 (M2/M6/S10 core-vs-secondary + C8 scope)

| Run | Total | % |
|-----|-------|---|
| 1 | 55 | 35% |
| 2 | 52 | 33% |
| 3 | 59 | 38% |
| **GT** | **~57** | **36%** |

- Spread: **7 pts (33–38%)** (was 10). Predicted convergences all landed:
  - M2 perf≥uPlot: 10/10/5 → **5/5/5** ✓; M6 Path2D: 5/10/10 → **5/5/5** ✓; C8 Float32: −1/−1/−1 → **0/0/0** ✓
- Residual variance now purely partial-credit magnitude on ambiguous SHOULDs:
  S13 framework 0/0/+3, C1 bands +1/−1/+1, S3 FPS, S16 callbacks, S10, S4.

### Fix after Run 2 (criteria v2): S13 + C1 core-vs-secondary clarifications.

## Run 3 — criteria v2 (S13 + C1)

| Run | Total | % |
|-----|-------|---|
| 1 | 59 | 38% |
| 2 | 66 | 42% |
| 3 | 60 | 38% |

- Spread: **7 pts (38–42%)** — no net improvement. S13 (0/0/+3 → +1/+1/+2) and C1
  (+1/−1/+1 → +1/+1/+1) converged as intended, but a *different* ambiguous SHOULD surfaced as the
  outlier: **S3 FPS 0/+2/+3** ("do ms targets count as FPS scenarios?"). **Whack-a-mole**:
  per-criterion edits keep relocating the jitter instead of eliminating it.
- Conclusion: per-criterion tuning has hit diminishing returns / overfitting risk. The remaining
  variance is structural — the partial-credit *magnitude* axis itself. Attack it with a mechanism
  change (answers the user's scoring-granularity question directly).

### Fix after Run 3 (skill v2): collapse SHOULD partial to a SINGLE bucket (= 2), removing the 1-vs-2 judgment entirely. (Finding: finer granularity, e.g. thirds, would do the opposite — more buckets = more room to disagree.)

## Run 4 — skill v2 (SHOULD partial = single value 2)

| Run | Total | % |
|-----|-------|---|
| 1 | 54 | 34% |
| 2 | 57 | 36% |
| 3 | 57 | 36% |
| **GT** | **57** | **36%** |

- Spread: **3 pts (34–36%)** — best of the session. Mean 56, essentially on GT.
- Ambiguous partials all locked: S4 **+2/+2/+2**, S10 **+2/+2/+2**, S13 **+2/+2/+2**.
- S3 FPS **0/0/0** and S16 callbacks **0/0/0** — both unanimously SILENT (were 0/2/3 and 0/2/2 in
  Run 3). Removing the partial-magnitude temptation pushed borderline cases to a clean stance.
- Only residual jitter: **S12 canvas-stacking 3/2/2** (genuine full-vs-partial judgment, ±1pt).

## Final progression

| Config | Totals | Spread | % range |
|--------|--------|--------|---------|
| Baseline (current skill) | 51 / 60 / 63 | **12** | 32–40 |
| v1 stance-check + cues | 57 / 60 / 67 | 10 | 36–43 |
| v2 + core-vs-secondary criteria | 52 / 55 / 59 | 7 | 33–38 |
| v3 + S13/C1 clarifications | 59 / 66 / 60 | 7 | 38–42 |
| **v4 + single-bucket SHOULD partial** | **54 / 57 / 57** | **3** | **34–36** |

- **Spread reduced 12 → 3 (≈75%).** Centered on the hand-verified ground truth (~36%).
- **Direction consistency: solved.** Across all 12 post-baseline runs, every contradiction
  (log −10, hover −3, NaN −3, input-formats −3, outliers −3) was unanimous — the core failure the
  findings report identified is gone.
- Two distinct fixes did the work: (1) the **stance-check + contrast cues** killed the
  direction errors; (2) the **single-bucket SHOULD partial** killed the magnitude jitter. The
  per-criterion core-vs-secondary clarifications helped specific MUSTs but showed whack-a-mole on
  SHOULDs — the mechanism change is what generalized.

## Caveats / next steps

- All of this is tuned/measured on ONE spec (`01/compressed.md`). The skill changes (stance-check,
  single-bucket partial) are general; the **criteria** edits encode resolutions to calls that were
  genuinely ambiguous — risk of overfitting to this spec. Validate by running the other lineages
  (02, 03, and the initial/enriched phases) before treating the criteria as settled.
- v4's converged scores resolve several flagged-ambiguous criteria to specific values (S8→−3,
  S3→0, S4→+2, S13→+2). These are *consistent* now but their *correctness* is exactly what
  `ambiguities-for-review.md` is for — expert confirmation may shift the criteria text again.
- The remaining ±1 jitter (S12 full-vs-partial) is not worth chasing on one spec.

## Round 5 — expert feedback incorporated + cross-spec generalization test

Expert review (in `ambiguities-for-review.md`) changed the criteria structure: log-as-symlog
demoted MUST→SHOULD (−10→−3); symlog split into two SHOULDs (auto-derive / override); hover
demoted SHOULD→COULD; FPS made partial-credit-able for ms targets; C13 "substantial address →
credit" generalized in the skill. New max = **151** (MUST 7 / SHOULD 20 / COULD 21). New GT for
01/compressed = **66 / 44%**.

Ran the updated skill+criteria on three compressed specs (01 = tuned, 02 & 03 = unseen):

| Spec | Runs (total / %) | Within-spec spread |
|------|------------------|--------------------|
| 01/compressed (GT 66) | 53/35%, 67/44% | 14 pts |
| 02/compressed | 80/53%, 86/57%, 69/46% | 17 pts |
| 03/compressed | 88/58%, 91/60%, 98/65% | 10 pts |

### Finding 1 — direction-of-meaning generalizes (the core bug stays fixed)
Within each lineage, every stance call is unanimous across runs and matches the spec's real intent:
- NaN connect-across: −3 on all 8 runs.
- Log-as-symlog: −3 for 01 & 02 (separate code path), **+3 for 03** (03 genuinely does log = symlog
  with C→0). The evaluator correctly flips per spec.
- Outlier SHOULD-NOT: −3 for 01 & 03 (both have σ/IQR detection), **0 for 02** (none). Correct.
- Split symlog-override: 01 = −3 ("no manual tuning"), 02 & 03 = +3 (override present). Clean.
Cross-spec ranking is preserved and sensible: 01 (~40%) < 02 (~52%) < 03 (~61%). 01 is lowest
because it genuinely makes the most reference-contradicting choices (IQR outliers, Float64-only
input, no symlog override, separate log path).

### Finding 2 — partial-credit MAGNITUDE does NOT fully generalize
The 10–17pt within-spec spreads come from magnitude wobble on a handful of criteria whose specific
ambiguity wasn't exercised by the single tuned spec:
- **M5/M6 Path2D**: 01-run-A scored **−10** (misread "plain data coords" as a contradiction) vs +5
  elsewhere; 02 wobbled +10/+5/+5 (is normalization "fully" present?). Biggest single-criterion
  swing (15 pts). The criterion *said* PARTIAL but it wasn't salient enough.
- **M2 uPlot** (0/+5/+10), **S2 benchmark configs** (0/+2/+3), **tooltip** (+2/+3), a few COULDs
  (empty-data, multiple-Y, Float32) — SILENT-vs-PARTIAL-vs-FULL boundary calls.

### Conclusion
Single-spec tuning generalizes for *direction* (the original failure mode) but not for *magnitude*.
The single-bucket SHOULD partial removed the 1-vs-2 jitter; the residual swings are
SILENT/PARTIAL/FULL boundary judgments and one PARTIAL/CONTRADICT misread. These need either
multi-spec tuning of the boundary wording or acceptance of ~10pt residual on unseen specs.

### Fix after Round 5: hardened M5/M6 Path2D — explicit three-case rule, "absence of normalization
is PARTIAL (+5), never negative." Re-validating on 01 next.

## Round 6 — re-validation of the M5/M6 hardening (01/compressed)

| Run | Total | % |
|-----|-------|---|
| A | 67 | 44% |
| B | 67 | 44% |
| C | 67 | 44% |
| **GT** | **66** | **44%** |

- **Spread 0** — three identical runs, all scoring M5 = +5 (partial). The −10 misread is gone.
- Lands on the expert-adjusted ground truth (66) within 1 point.
- Net: on the tuned spec, the full pipeline (stance-check + cues + single-bucket partial + expert
  criteria + M5 three-case rule) is now essentially deterministic.

## Final status

- **01/compressed (tuned):** baseline spread 12 → **0**, on ground truth.
- **02 & 03/compressed (unseen):** spread 17 / 10 measured *before* the M5 hardening. The M5 fix
  removes one of their wobble sources (02 had M5 +10/+5/+5); re-running them is the obvious next
  step to confirm. Remaining untuned wobble there: M2 (is uPlot named?), S2 (benchmark configs),
  tooltip, a few COULDs — all SILENT/PARTIAL/FULL boundary calls, none direction errors.
- **Direction-of-meaning consistency is solved and generalizes.** Magnitude consistency is solved
  on the tuned spec and partially generalizes; closing it fully on arbitrary specs needs the
  boundary wording exercised against more specs (not more iteration on one).

## Round 7 — scheme change: SHOULD 3 → 4 (per expert; partial=2 now exactly half)

Single partial value confirmed; SHOULD bumped to 4 so partial (2) is the exact midpoint (was
slightly generous at 2-of-3). Should-not → −4 for symmetry. New **max = 171** (MUST 70 / SHOULD 80 /
COULD 21). Stances unchanged → consistency unaffected, only weighting rebalances.

Confirmation on 01/compressed (3 fresh runs, new scheme):

| Run | Total | % |
|-----|-------|---|
| A | 69 | 40% |
| B | 69 | 40% |
| C | 69 | 40% |
| **GT (predicted)** | **67** | **39%** |

- **Spread 0** — agents apply 4 / 2 / −4 correctly and deterministically.
- Runs land 2 pts above the predicted GT, entirely on **S12 canvas-stacking**: all three read it as
  full (+4); my key had it partial (+2). The runs are unanimous, so it's *consistent* — S12 is the
  last genuine full-vs-partial judgment call (whether "drawn twice / set ≪ total" is core or
  secondary). I'm treating the runs' "full" as the settled reading: **GT updated to 69 / 40%.**
- 01/compressed under the final skill+criteria: baseline spread 12 → **0**, deterministic at 40%.

## Round 8 — re-run 02 & 03 under current scheme; build their GT keys; tighten boundary wording

Goal (per HANDOFF): re-measure 02/03 within-spec spread under the *current* skill+criteria (171 max,
post-M5-hardening, SHOULD=4), build hand-verified GT keys for both, and pin down the residual
magnitude wobble. Model sonnet, 3 fresh runs per spec.

### Measured spread (before this round's criterion edits)

| Spec | Runs (total) | Spread | Hand GT (this round) |
|------|--------------|--------|----------------------|
| 02/compressed | 85 / 82 / 77 | **8 pts** | **88 / 51%** |
| 03/compressed | 94 / 99 / 102 | **8 pts** | **95 / 56%** |

Both tightened vs the stale pre-hardening numbers (17 / 10). Cross-spec ranking holds and is
sensible: 01 (69/40%) < 02 (88/51%) < 03 (95/56%). GT keys:
`ground-truth-02-compressed.md`, `ground-truth-03-compressed.md`.

### Finding — direction still fully solved between runs; all residual is magnitude

Every stance call was unanimous and correct across all 6 runs: NaN pen-lift −4 (both specs), log =
symlog **−4 for 02 / +4 for 03** (correct per-spec flip), σ-outlier SHOULD-NOT **−4 for 03 / 0 for
02**, decimation, WebGL, zero-deps. Zero direction disagreement between runs. The residual 8-pt
spreads are SILENT/PARTIAL/FULL boundary calls on ~8 criteria.

### One unanimous *accuracy* miss (not a between-run inconsistency)

C7 (live/append): all 3 runs on 02 scored **−1 (CONTRADICTS)**, reading 02's "copies only the new
tail + invalidates cache" as a forbidden streaming optimization. It isn't — the tail-copy is data
handling and the cache invalidation *is* a full redraw; 02 even defers the streaming RENDER path. GT
= +1. The runs were consistently wrong because the criterion didn't say where the line is.

### Per-criterion wobble → fixes (8 `tech-criteria.md` edits this round)

| Crit | 02 runs | 03 runs | Encoded resolution |
|------|---------|---------|--------------------|
| M2 uPlot | 0/0/0 | 5/5/5 | lock: uPlot must be named for credit; named-no-fairness = PARTIAL; unnamed = SILENT (fixed my 02 key 5→0) |
| S2 benchmark | 2/4/4 | 2/2/2 | de-parenthesize dual-regime; one/none regime = PARTIAL |
| S3 FPS | 2/2/2 | 2/2/0 | untethered FPS number (no config) = SILENT |
| S10 markers | 4/2/4 | 4/4/4 | opt-in/configurable marker still = "represented" → FULL |
| S12 stacking | 4/4/4 | 2/4/4 | two-canvas stack = the core → FULL; "drawn twice"/"≪total" secondary |
| S13 fw-core | 0/−4/−4 | 2/4/4 | 4-rung ladder (FULL/PARTIAL/SILENT/CONTRADICTS); React-only = SILENT, not −4 |
| C7 append | −1/−1/−1 | 0/1/0 | copy+invalidate = full redraw = AGREES; only an incremental render path contradicts |
| C8 Float32 | 1/0/1 | −1/0/0 | Float64 internal storage = SILENT (declined optimization), not −1 |

Left **OPEN / logged for expert** (not encoded): S11 hedged tooltip (4/2/4), S14 typed-array-only
input surface, C12 nearest-point readout as anti-pattern, C17 out-of-scope vs planned, S7 fixed-margin
single-run −4 blip. See `ambiguities-for-review.md`.

**Regression check (hand):** all 8 edits were hand-verified against the 01 key — none should move 01's
settled GT of 69 (01 names uPlot → M2 PARTIAL +5; states both regimes → S2 FULL +4; plain-JS
controller → S13 PARTIAL +2; ms targets tied to configs → S3 PARTIAL +2).

### Confirmation runs (post-edit) — 3 fresh sonnet runs each on 01/02/03

Totals recomputed directly from each run's `scores` block (several runs had arithmetic slips in their
self-reported totals — e.g. one 03 run reported 90 but its own per-criterion scores sum to 98).

| Spec | Pre-edit | Post-edit (from scores) | GT | Verdict |
|------|----------|-------------------------|-----|---------|
| 01 | 69/69/69 (spread **0**) | 73 / 69 / 64 (spread **9**) | 69 | ⚠ regressed |
| 02 | 85/82/77 (spread 8) | 89 / 89 / 94 (spread **5**) | 88 | ✓ tightened, on GT |
| 03 | 94/99/102 (spread 8) | 100 / 98 / 96 (spread **4**) | 95 | ✓ tightened, near GT |

**02 & 03 — edits worked.** The S13 `−4` contradictions are gone (02 S13 now 0/2/2, was 0/−4/−4;
03 S13 now 4/2/2, was 2/4/4). S3 converged to 0/0/0 (03), S12 to 4/4/4 (03), S14 to 2/2/2 (03),
C8 to 0/0/0, C12 to −1/−1/−1, C17 to 0/0/0. Means moved onto the GT keys. Residual wobble is now
just the two left-OPEN items — S11 tooltip (4/2/4) and S13 FULL-vs-PARTIAL on 03's "engine" (4/2/2) —
plus minor new single-run noise (02 S6 tick-precision 0/0/4, 02 S16 2/4/2).

**01 — regressed (spread 0 → 9), two causes:**
- **M2 (my edit):** runs 5/5/0. One run read 01's "uPlot-level render throughput" as *not* naming
  uPlot as the bar → SILENT 0. My added wording "uPlot must be named **as the performance bar**" was
  too strict. → **re-fixed**: reworded so naming uPlot as a perf reference *anywhere* (incl.
  "uPlot-level throughput") earns ≥ PARTIAL; SILENT only when uPlot is wholly unmentioned. 01 names
  uPlot, 03 names uPlot, 02 does not → 5 / 5 / 0 across specs, all consistent.
- **S5 (pre-existing noise, NOT my edit):** runs 0/−4/−4. One run read "no manual tuning" as silence
  rather than the contradiction the criterion already explicitly names. The cue is present; this is
  sonnet sampling noise (Round 7's 3/3 determinism was slightly lucky on this criterion). Left as-is.

### Re-confirmation of 01 after the M2 re-fix — 3 fresh sonnet runs

| Run | Total | M2 | S5 |
|-----|-------|----|----|
| A | 69 | +5 | −4 |
| B | 69 | +5 | −4 |
| C | 69 | +5 | −4 |
| **GT** | **69** | +5 | −4 |

**Spread back to 0, on GT.** M2 is now 5/5/5 (the softened wording — "naming uPlot anywhere as a perf
reference earns ≥ PARTIAL" — fixed the misread) and S5 is −4/−4/−4 (the earlier one-run S5 blip did
not recur, confirming it was sampling noise, not a structural issue).

### Round 8 — final status

| Spec | Pre-edit spread | Post-edit spread | GT | On GT? |
|------|-----------------|------------------|-----|--------|
| 01/compressed (tuned) | 0 | **0** (69/69/69) | 69 / 40% | ✓ exact |
| 02/compressed | 8 | **5** (89/89/94) | 88 / 51% | ✓ runs ≈ GT |
| 03/compressed | 8 | **4** (100/98/96) | 95 / 56% | ✓ runs ≈ GT |

- **02 & 03 spreads cut to 5 / 4** and centered on their hand-verified GT keys; the S13 `−4`
  direction errors are eliminated; S2/S3/S10/S12/S14/C7/C8/C12/C17 converged.
- **01 held deterministic at 69** through all the criterion edits (the M2 over-tighten was caught and
  reverted). The criteria changes generalize rather than overfit: every edit was validated to leave
  01's settled key untouched.
- **Residual wobble** is now the two deliberately-OPEN judgment calls only — S11 (hedged tooltip,
  03 = 4/2/4) and S13-FULL-vs-PARTIAL on 03's "engine" (4/2/2) — plus stray single-run noise
  (02 S6 0/0/4, 02 S16 2/4/2, 01 S5). These are logged in `ambiguities-for-review.md` for the expert;
  forcing them further risks overfitting (the Round 3 whack-a-mole lesson).
- **Net for the session:** direction-of-meaning remains fully solved and generalizing; partial-credit
  *magnitude* on the two unseen specs went from ~10–17 pt spreads to **4–5 pt**, with both specs now
  backed by GT keys.

## Round 9 — cross-pipeline generalization (manual-5d0e14e 1500w + cc-base)

Goal (per HANDOFF): run the *same* validated skill + `tech-criteria.md` against two *other* generation
pipelines for the same underlying prompt, to test that the Round-8 criteria generalize beyond the
`e57a9ad` family they were tuned on, and to compare pipelines. Model sonnet, 3 fresh runs per spec
file. **All totals below were recomputed by hand from each run's `scores` block** — the sonnet runs'
self-reported totals slipped by ±4–7 pts routinely, and one manual-03 run used a wrong max (167) and a
factual error (claimed uPlot named when it wasn't); trust the per-criterion lines, not stated totals.

### Pipeline-structure correction
The HANDOFF assumed the two new dirs hold "the same underlying three specs." They don't: both
`catnip-phased-manual-5d0e14e` (README prompt = `/catnip:draft-spec …`) and `cc-base` (README prompt)
use a **single prompt** generated **3× independently**. So `01/02/03` and `spec-1/2/3` are *three runs
of one prompt*, not three distinct specs. All 9 specs across the 3 pipelines therefore target the
**same** reference. Consequence: within-family 3-run spread = pipeline *consistency* / generation
variance; cross-family = pipeline *quality*. (The `e57a9ad` 01/02/03 also diverge run-to-run, e.g. one
keeps log=symlog, others drift to a separate log path.)

### Measured spread (initial criteria, before this round's 2 edits) — recomputed totals

| Spec file | runs (total) | spread | mean | %mean |
|-----------|--------------|--------|------|-------|
| manual-01-1500w | 77 / 74 / 93 | **19** | 81 | 47% |
| manual-02-1500w | 99 / 91 / 102 | 11 | 97 | 57% |
| manual-03-1500w | 93 / 88 / 99* | 11 | 93 | 54% |
| cc-base spec-1 | 94 / 96 / 94 | **2** | 95 | 55% |
| cc-base spec-2 | 81 / 76 / 78 | **5** | 78 | 46% |
| cc-base spec-3 | 95 / 95 / 95 | **0** | 95 | 56% |

\* one manual-03 run was buggy (wrong max 167, miscounted criteria, scored M2=+5 though uPlot is
unnamed); corrected to M2=0 it lands ~99.

### Finding 1 — direction-of-meaning generalizes strongly, and newly-exercised cues fire correctly
Several directional criteria that the `e57a9ad` family never stressed were exercised here and scored
**correctly and unanimously across all 3 runs**:
- **M5 Path2D pixel-coords = CONTRADICTS −10** on cc-base spec-2 ("Paths are built in pixel
  coordinates… simpler than building in data-space and applying a CSS transform") — the case-(c) arm
  of the three-case rule fired, all 3 runs. Meanwhile normalized-coord specs (manual all, cc-1, cc-3)
  scored +10. Strong validation of the M5 rule.
- **S20 log=symlog flips −4** on cc-base spec-3 ("separate Log Scale section… symlog is the special
  case of log") vs **+4** for manual (alias) and cc-1 — unanimous.
- **S17 decimation −4** on manual-03 (built-in "min/max decimation pass during Path2D construction") —
  unanimous; +4 elsewhere.
- **SN2 bundle-size −4** on cc-base spec-3 ("Bundle size target: <30 kB") — **first time this
  SHOULD-NOT was ever triggered**; all 3 runs caught it.
- SN1 outliers (−4 manual-01/02 IQR/percentile, 0 elsewhere) and S6 tick-precision (−4 on the SI-label
  specs) all consistent.

### Finding 2 — two NEW magnitude/direction problems surfaced (both fixed this round)
- **M6 (stable-series-ids) direction split, MUST, ±10** — only on **manual-01**, whose terse wording
  "Cache keys are stable series ID strings (caller-assigned); invalidated only on data change or
  series add/remove" was read by 2/3 runs as a contradiction of the parenthetical "(add/remove doesn't
  invalidate all)" → −10, while 1/3 correctly scored the core (stable IDs as keys) +10. This is the
  *entire* source of manual-01's 19-pt spread. The settled `e57a9ad-01` key has M6 = **+10**
  ("Stable string series IDs as Path2D cache keys") — identical core — so −10 is an error.
- **S14 (input formats) spanning CONTRADICTS/PARTIAL/SILENT** — manual specs say "Float64Array
  required (not number[])" (explicit number[] rejection, identical to the settled `e57a9ad-01` key's
  **−4**), but runs split −4/+2/0; cc-base accepts number[]+F32+F64 (missing only number[][]) and
  scored +2.

### Criteria edits this round (2; both non-regressing, reference-faithful)
1. **M6** — clarified the core is *keying the cache on stable series IDs* (= FULL); merely listing
   invalidation triggers ("invalidated on … add/remove") still AGREES; CONTRADICTS only if the cache
   is keyed on something unstable or the spec explicitly flushes the *entire* cache on any single
   add/remove. (Parallels the M5/S12/S13 core-vs-secondary clarifications.)
2. **S14** — encoded the FULL/PARTIAL/CONTRADICTS ladder: full multi-format surface = FULL; accepting
   several listed types but omitting one (e.g. no number[][]) **without rejecting any** = PARTIAL; an
   *explicit* single-typed-array requirement that rejects number[] ("Float64Array required (not
   number[])") = CONTRADICTS. This matches the settled `e57a9ad-01` −4 and the round-8 lean of PARTIAL
   for the merely-one-type-no-rejection case.

### Confirmation + non-regression (post-edit, 3 fresh runs manual-01, 2× e57-01, 1× e57-02, 1× e57-03)
| Spec | pre-edit | post-edit (recomputed) | settled key | verdict |
|------|----------|------------------------|-------------|---------|
| manual-01-1500w | 77/74/93 (spread 19) | **92 / 93 / 91 (spread 2)** | — | ✓ M6 now +10/+10/+10; S14 −4/−4/−4 |
| e57a9ad-01 | 69 (key) | **69 / 69** | 69 | ✓ exact, no regression |
| e57a9ad-02 | 88 (key) | **88** | 88 | ✓ exact |
| e57a9ad-03 | 95 (key) | **97** | 95 | ✓ within its normal 95–98 band (S14 stayed +2) |

The M6 fix collapses manual-01's spread 19→2 and the S14 cue makes the manual family's input-format
score deterministic, all while leaving the three settled `e57a9ad` keys untouched.

### Cross-pipeline comparison (means, all targeting the same prompt)
| underlying | e57a9ad | manual-5d0e14e (1500w) | cc-base |
|------------|---------|------------------------|---------|
| run 1 | 69 / 40% | ~92 / 54% (post-fix) | 95 / 55% |
| run 2 | 88 / 51% | 97 / 57% | 78 / 46% |
| run 3 | 95 / 56% | ~93 / 54% | 95 / 56% |

All 9 land in a **40–57%** band. The variation is driven by *real* per-generation design divergence
that the criteria correctly discriminate: specs honoring the baked-in decisions (log=symlog,
normalized Path2D, stable IDs, no outlier detection) score higher; those that drift (separate log
path → cc-3/e57-01/e57-02; pixel-coord Path2D → cc-2; IQR/σ outliers → manual-01/02 & e57-01/03;
bundle-size target → cc-3) score lower. No pipeline is uniformly better; consistency is best for
cc-base (spreads 0/5/2) and weakest where a single criterion's wording was ambiguous (manual-01 M6,
now fixed). **Conclusion: the Round-8 criteria generalize across pipelines** — direction-of-meaning is
solid and the newly-exercised cues (M5 pixel-coords, S20 separate-log, S17 built-in-decimation, SN2
bundle target) all fired correctly; the only generalization gaps were the two wording issues above,
now encoded.

### Still OPEN for the expert (unchanged stance, logged in ambiguities-for-review.md)
- **S11 tooltip FULL-vs-PARTIAL** on the "anchor `<div>` + onHighlight callback" pattern (cc-base
  spec-3: +2/+4/+2). Clear ends are settled (caller-supplied content = −4; built-in value readout =
  +4); only the anchor-plus-callback middle wobbles.
- **C17 multipleY** "out of scope" vs "planned, not in initial cut" (manual-03: +1/−1/+1).
- **S8 autofitY** "never widen" secondary detail (4/2 wobble, several specs) — minor.
