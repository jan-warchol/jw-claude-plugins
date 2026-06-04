# Ambiguous scoring calls — for expert review

These are criteria where the "correct" score for `01/compressed.md` is genuinely
debatable (domain judgment or criterion-interpretation calls), independent of the
evaluator-consistency work. Jan to review with his more-expert friend. Each lists the
range I considered and the call I recorded in the ground truth.

Two categories of ambiguity are intertwined and worth separating in review:
- **(I) Interpretation of the criterion** — what does the criterion actually require?
- **(D) Domain judgment** — given the spec text, did it satisfy that requirement?

> **Status note (after the consistency work):** to make scoring *consistent*, the criteria were
> edited to encode a specific resolution for several of these. That makes runs agree — it does
> **not** make the chosen value correct. Each row below is tagged **[ENCODED → x]** where the
> criteria now steer the evaluator to value `x`; if you disagree, change the cue in
> `tech-criteria.md` (and, for M4, decide the −10-vs-0 question). Rows without the tag are still
> fully open.

---

# New calls surfaced on specs 02 & 03 (Round 8)

All of these are SILENT/PARTIAL/FULL *magnitude* boundaries (direction-of-meaning is unanimous and
correct across all runs). Where the reference is clearly on one side I tightened `tech-criteria.md`
this round and tag it **[ENCODED → x]**; the genuinely-debatable ones are left **OPEN** for you.

## M2 — Performance ≥ uPlot, when uPlot is NOT named (spec 02)

- 02 gives concrete perf targets (≤5 ms draw @100k pts, 60 Hz) but never names uPlot. All 3 runs
  scored **0 (SILENT)**; my first 02 key had **+5**. **[ENCODED → 0]**
- Resolution encoded: uPlot must be *named* to earn any credit; a generic numeric perf goal is not
  the "≥ uPlot" core → SILENT. (03 names uPlot but omits the decimation-fairness point → PARTIAL +5;
  all 3 runs agreed.) If you think a strong standalone perf target deserves partial credit even
  without naming uPlot, soften this. Otherwise the rule is now consistent.

## M2 — decimation-fairness wording (spec 03)

- 03: "initial render ≥ uPlot (no client decimation)". Is "(no client decimation)" the
  decimation-*fairness* point (uPlot-with-decimation excluded as cheating → FULL) or just the
  library's own no-decimation stance (→ PARTIAL)? All 3 runs read PARTIAL **+5**. **[ENCODED → 5]**
- Open-ish: terse phrasing; defensibly FULL. Low stakes (5 vs 10 on one MUST). Flagging.

## S2 — Main benchmark: one regime vs both (specs 02 & 03)

- Criterion lists both regimes (few-series-many-pts AND many-series-few-pts). 02 states neither;
  03 states one ("100 series × 1k"). Runs split on 02 (2/4/4), unanimous PARTIAL on 03 (2/2/2).
  **[ENCODED → 2]** for both.
- Resolution encoded: de-parenthesized the dual-regime and made it a *required* element — FULL needs
  100k/chart AND both regimes; one or none = PARTIAL. (01 states both → stays FULL +4, no regression.)
  Question (I): is the dual-regime really core, or is the 100k/chart headline enough for full credit?

## S3 — bare FPS number not tied to a config (spec 03)

- 03: "zoom/pan ≥ Dygraphs (60fps)" — an FPS number with no point-count/series config attached.
  Runs split 2/2/0. **[ENCODED → 0]**
- Resolution encoded: the "tied to specific configs" element is required even for PARTIAL; an
  untethered FPS/perf number is SILENT. (02's ≤5 ms IS tied to 100k pts → stays PARTIAL +2; 01's ms
  targets are tied to configs → stays PARTIAL +2, no regression.)

## S11 — minimal/hedged tooltip (spec 03) — OPEN-ish

- 03: a "tooltip anchor" + "minimal crosshair + nearest-point readout assumed in scope" (buried in
  Uncertainty). Runs split 4/2/4. Recorded **+2 (PARTIAL)**.
- Question (I/D): does an acknowledged-but-unspecified, anchor-only readout meet "at least basic; not
  deferred to the consumer" (→ FULL), or is it too thin (→ PARTIAL)? I lean PARTIAL (hedged, in
  Uncertainty). Not yet encoded — flag for your call.

## S13 — framework-agnostic core: the full stance ladder (specs 02 & 03)

- 02 is entirely React (controller is a React hook): runs split **0 / −4 / −4**. 03 has a
  framework-neutral controller but React rendering: runs split **2 / 4 / 4**. **[ENCODED → ladder]**
- Resolution encoded (general, reference-faithful ladder): FULL = framework-neutral *rendering* core
  + thin React wrapper; PARTIAL = neutral controller only / core not clearly separable; SILENT =
  all-React, no neutral element (NOT a contradiction); CONTRADICTS = argues against a neutral core.
  → 02 = SILENT 0, 03 = PARTIAL 2. (01 plain-JS controller + React render → PARTIAL +2, no regression.)
- This was the single biggest swing source (±4 in both specs); please sanity-check the ladder.

## S14 — typed-array-only input surface (specs 02 & 03) — OPEN

- Both specs specify one input type + internal copy/coerce + the sorted-by-X assumption, but neither
  offers the full multi-format surface (number[], number[][], …). Runs split 2/2/0 (02) and 0/2/2 (03).
  Recorded **+2 (PARTIAL)**.
- Question (I): is "picks one input type, copies internally, assumes sorted" PARTIAL engagement with
  the multi-format criterion, or SILENT on it? I lean PARTIAL. Not encoded — flag.

## C7 — append handling read as a streaming-opt contradiction (spec 02)

- 02: "Incremental append … copies only the new tail, increments dataVersion, invalidates path cache"
  + "ring-buffer path extension … deferred". All 3 runs scored **−1 (CONTRADICTS)**; correct read is
  **+1 (AGREES)** — the data-side tail-copy still triggers a full redraw (cache invalidated), and the
  streaming RENDER path is explicitly deferred. **[ENCODED → +1]**
- Resolution encoded: clarified that copy-appended-data-then-invalidate-cache = full redraw = AGREES;
  only a dedicated incremental RENDER path that avoids the redraw contradicts. (This was a *direction*
  miss the runs made unanimously — the only one this round — caused by criterion wording, not the skill.)

## C8 — Float64 internal storage = SILENT, not contradiction (spec 03)

- 03 stores internally as Float64. One run scored **−1 (CONTRADICTS)**; correct is **0 (SILENT)**.
  **[ENCODED → 0]** — clarified that declining the optional Float32 optimization is silence, not
  opposition (it's a COULD, nothing to contradict). (02 stores Y as Float32 → +1.)

## C12 — "nearest-point readout" as the hover anti-pattern (spec 03) — OPEN

- 03: "nearest-point readout assumed in scope". Is that the snapping anti-pattern the criterion names
  (→ CONTRADICTS −1) or just a tooltip readout, silent on the highlight hit-test mechanism (→ 0)?
  Runs split −1/0/−1. Recorded **−1** (majority) but defensibly SILENT. Not encoded — flag.

## C17 — "out of scope" vs "planned, not initial" (spec 03) — OPEN-ish

- 03 lists "per-series independent y-axes" in Out of Scope (excluded, no future plan). The criterion
  says "planned, not in initial cut". Runs split 0/1/0. Recorded **0 (SILENT)** — excluded-entirely
  ≠ planned-for-later. Low stakes (1 pt). Flag.

## S7 — fixed margins read as contradicting adaptive Y-width (spec 02) — single-run blip (pre-Round-9)

- One 02 run scored the axis-labels criterion **−4 (CONTRADICTS)** because 02 uses "fixed margins
  (48px Y)". Correct is **0 (SILENT)**: 02 is silent on the label-robustness *core*; rejecting the
  adaptive-width *secondary* detail does not make it a contradiction. Only 1 of 3 runs erred; left as
  a note (no criterion change) — watch whether it recurs.

---

# New calls surfaced on the manual-5d0e14e and cc-base pipelines (Round 9)

All 9 specs (3 pipelines × 3 runs) target the same prompt. Two wording problems were ENCODED this
round (non-regressing vs the settled e57a9ad keys 69/88/95); three are left OPEN for the expert.

## M6 — stable-series-ids read as a contradiction (manual-01) — ENCODED → AGREES/FULL
- manual-01: "Cache keys are stable series ID strings (caller-assigned); invalidated only on data
  change or series add/remove." Runs split **−10 / −10 / +10** (a MUST direction split, the whole
  source of manual-01's 19-pt spread). The settled e57a9ad-01 key has M6 = **+10** ("Stable string
  series IDs as Path2D cache keys") — identical core — so −10 is an error.
- **[ENCODED → FULL]**: criterion now says keying the cache on stable series IDs IS the core (FULL);
  listing invalidation triggers ("invalidated on … add/remove") still AGREES; CONTRADICTS only if
  keyed on something unstable or the spec flushes the *entire* cache on any single add/remove.
  Post-fix: manual-01 M6 = +10/+10/+10, spread 19→2; e57a9ad-01 unchanged at 69. Sanity-check welcome.

## S14 — input formats: explicit number[] rejection vs missing-one-format (all pipelines) — ENCODED → ladder
- manual specs: "Float64Array required (not number[])" (explicit rejection, identical to e57a9ad-01's
  settled **−4**) — but runs split −4/+2/0. cc-base: accepts number[]+F32+F64, missing only number[][]
  → +2. e57a9ad-02/03: "coerce to Float64Array" without rejecting number[] → +2 (round-8 lean).
- **[ENCODED → ladder]**: full multi-format surface = FULL; accept several listed types but omit one,
  *without rejecting any* = PARTIAL (+2); *explicit* single-typed-array requirement rejecting number[]
  ("Float64Array required (not number[])") = CONTRADICTS (−4). Non-regressing: e57-01 stays −4,
  e57-02/03 stay +2, manual all → −4 (consistent), cc-base → +2. Confirm the "explicit-rejection =
  contradiction" call (round-8 had leaned PARTIAL for the no-rejection case only — this resolves the
  *explicit-rejection* case the other way, consistent with the e57-01 key).

## S11 — tooltip "anchor <div> + onHighlight callback" (cc-base spec-3) — OPEN
- cc-base spec-3 has a DOM "tooltip anchor" + an onHighlight callback carrying values, but no
  built-in rendered tooltip. Runs split **+2 / +4 / +2**. The clear ends are settled (caller-supplied
  *content* = −4, as manual-01; built-in value readout = +4, as manual-03 "tooltip lists all series
  values"); only this anchor-plus-callback middle wobbles. I lean PARTIAL. Not encoded — same family
  as the round-8 S11 hedged-tooltip OPEN item.

## C17 — "out of scope" vs "planned, not in initial cut" (manual-03) — OPEN (recurs from round 8)
- manual-03 puts multiple-Y "out of scope"; runs split **+1 / −1 / +1** (AGREES vs CONTRADICTS). Same
  ambiguity as the round-8 C17 item (03's per-series y-axes in Out of Scope). Still un-encoded; low
  stakes (1 pt).

## S8 — autofit-Y "never widen" secondary detail (several specs) — OPEN, minor
- "Y auto-fits to visible X range" present but the "can only narrow last user-set Y range, never
  widen" constraint absent → FULL-vs-PARTIAL wobble (4/2) across manual-02/03 and others. Minor.
