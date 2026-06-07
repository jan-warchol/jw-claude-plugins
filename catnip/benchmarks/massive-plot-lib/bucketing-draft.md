# Bucketing draft — massive-plot-lib

**Status:** draft by Claude for expert review. **Not authoritative.**

This re-partitions the reference spec's content into five buckets. It replaces the presence-based
`tech-criteria.md` (which baked the author's interchangeable architecture choices in at the `MUST`
tier — see "Corrections" at the end).

## The buckets and how each is scored

| Bucket            | Definition                                                                          | Scoring rule                                                                                                          |
| ----------------- | ----------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **1. Prompt**     | Genuine user-side knowledge — the _problem_. Becomes the thinned prompt.            | Not scored; it's the input.                                                                                           |
| **2. Must-ask**   | Resolution needs something only the user can supply.                                | Score on **whether it was asked / surfaced**. A correct _silent_ guess earns **no credit** (boundary cases: penalty). |
| **3. Deducible**  | One clear best answer derivable from domain knowledge.                              | Score on **decision present & sound**. Asking the user = mild waste.                                                  |
| **4. Raise-only** | Must appear; any reasonable resolution (or an explicit "pick one of A/B/C") counts. | Score on **topic surfaced**, not which answer.                                                                        |
| **5. Drop**       | Pure opinion or low-level technique.                                                | Not a criterion.                                                                                                      |

**Must-ask has two flavors:**

- `[stated]` — the user knows the question exists, just hasn't answered it.
- `[blind-spot]` — the user doesn't know the question exists. Knowledge's job is to _find and
  frame_ the trade-off; the user still owns the answer. This is where leaning on model knowledge
  and not-silently-deciding coexist: knowledge surfaces, it does not decide.

> ⚑ = **expert ruling needed.** I am the wrong one to draw the must-ask ↔ deducible line, because
> I'll classify as "deducible" exactly what models like me are confident about — which shrinks
> must-ask and flatters CATNIP. Treat every ⚑ as "Claude says deducible/decided; confirm it isn't
> really must-ask." All of Bucket 3 is implicitly ⚑.

---

## Bucket 1 — Prompt (problem facts, not scored)

These are things a real ML-dashboard author would actually walk in knowing. Solution decisions
have been stripped out and reassigned below.

- Domain: charting library for ML experiment dashboards (Neptune/W&B-style).
- Scale of display: 100+ charts loaded, 100+ visible at once.
- Scale per chart: hundreds of series; originals 1M+ points, **pre-aggregated server-side to ~100k
  points/chart** before reaching the browser.
- Primary task: **spot outliers** across the pack of similar series (individual lines aren't
  readable at that density; the pack's shape is).
- Show **non-finite values (NaN/±Inf)** because they flag bugs in a run.
- Zoom in to recover detail aggregation hid; **zoom + hover-highlight synced across all charts**.
- Data spans **many orders of magnitude and is not all positive** → a plain log scale won't cover
  it.
- Series cover **different X subsets** (sparse logging, early-terminating/crashed runs) — they
  don't share one set of X values.
- Performance bar: **≥ uPlot**, more responsive than Dygraphs; **no data-discarding decimation**
  (outlier-spotting forbids misrepresenting the data).
- Web, **React**, as few runtime deps as possible.

---

## Bucket 2 — Must-ask

| #   | Item                                                                                                                       | Flavor         | Note                                                                                                                                                                                          |
| --- | -------------------------------------------------------------------------------------------------------------------------- | -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| M1  | **NaN / missing-point rendering**: leave gaps vs. connect across vs. dedicated markers                                     | `[stated]`     | The expert's own canonical "to be decided by the user" example. No knowledge-derivable right answer; it's a visual preference.                                                                |
| M2  | **Concrete performance targets** — actual FPS thresholds and the specific series×points×chart scenarios that must hit them | `[stated]`     | The _scales_ are in the prompt; the _acceptance numbers_ live in the author's head (Neptune experience). CATNIP may propose and confirm.                                                      |
| M3  | **Reversed / single-value range behavior** (reverse-render vs. auto-sort vs. degenerate)                                   | `[stated]`     | Spec itself marks this TBD; genuine preference. ⚑ could be demoted to raise-only.                                                                                                             |
| M4  | **Initial axis-range sync across charts**                                                                                  | `[blind-spot]` | User asked for _synced_ zoom/highlight. Syncing _initial_ ranges on async-loading data causes a re-render/blink storm. Surface the trade-off; recommend pushing initial sync to the consumer. |
| M5  | **Framework-agnostic core vs. React-only at V0**                                                                           | `[blind-spot]` | Real effort-now vs. future-flexibility trade-off the user likely hasn't weighed. Recommend, don't silently pick.                                                                              |
| M6  | **Assume sorted input?**                                                                                                   | `[blind-spot]` | Large perf/simplicity win vs. silent breakage on unsorted data. Surface; recommend assume-sorted. ⚑ arguably deducible.                                                                       |
| M7  | **Canvas visual-regression testing is inherently flaky** (hardware/AA/impl differences)                                    | `[blind-spot]` | Surface that a real testing-strategy cost exists; recommend an approach. ⚑ could be raise-only.                                                                                               |
| M8  | **"Push concerns to the consumer" stance** (decimation, axis sync, …) — a deliberate not-a-generic-tool trade-off          | `[blind-spot]` | Surface & confirm the user accepts a specialized, less-batteries-included library. ⚑ overlaps M4.                                                                                             |

---

## Bucket 3 — Deducible (all ⚑)

One clear best answer a competent model can supply; scored on the _decision_, not on asking. Every
line here is a candidate for promotion to must-ask if the expert disagrees that the answer is
knowledge-derivable.

| #   | Item                                                                                               | Why I call it deducible (contestable)                                                                                                          |
| --- | -------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| D1  | **Independent X array per series**                                                                 | Forced by "series have different X subsets" — shared-X is impossible/wasteful here.                                                            |
| D2  | **Symlog** as the mechanism for log-on-non-positive data; auto-derived params with manual override | matplotlib precedent; "log of non-positive" has a known best answer. The _name_ symlog is the deduced solution to the prompt's stated problem. |
| D3  | Accept `number[]` / typed arrays; require random access (no lazy iterables)                        | Standard; follows from "iterate multiple times".                                                                                               |
| D4  | Auto-fit to data with configurable padding                                                         | Baseline expectation.                                                                                                                          |
| D5  | DPR handling + `ResizeObserver` + raster-size cap                                                  | Standard canvas-correctness; forced by "many charts, any screen".                                                                              |
| D6  | Robustness contract: type-correct never crashes, clearly-malformed throws with a message           | Standard library hygiene.                                                                                                                      |
| D7  | Empty-data fallback axis range                                                                     | Trivial correctness detail.                                                                                                                    |
| D8  | ESM-only, browser-only, React as peer dep                                                          | Modern default given "web, React, minimal deps".                                                                                               |
| D9  | Virtualize off-viewport charts                                                                     | Forced by "100+ loaded, 100+ visible".                                                                                                         |
| D10 | A minimal built-in color palette                                                                   | Needed for "usable with minimal config".                                                                                                       |
| D11 | Clamp zoom at float resolution (can't zoom below precision)                                        | Known numeric edge; one sane behavior.                                                                                                         |

---

## Bucket 4 — Raise-only (topic must appear; any reasonable resolution)

Scored on whether the spec _engages_ the topic — a decision **or** an explicit "options are A/B/C,
pick one" both count.

- Mark types beyond lines: **points**, **bands / error-bounds**.
- **Axis-label quality**: ≥2 labels, no repeat/overlap/overflow, nice decimals, adaptive Y-axis
  width.
- **Number formatting**: precision + scientific-notation threshold.
- **Time / date scales** (even if best-effort or deferred).
- **Tooltip / crosshair / legend** — presence and rough ambition.
- **Hover hit-testing** approach (e.g. interpolated y at hovered x, with a fallback).
- **Auto-fit Y under X-zoom** behavior.
- **Render-performance strategy** — _some_ caching scheme (not which one).
- **Highlight-performance strategy** — _some_ overlay/redraw scheme (not which one).
- **Theming** approach.
- **Extreme-range / very-large-magnitude** handling.
- A real **out-of-scope** section exists.
- **Staging / milestones** — the spec phases the work rather than treating it as one lump.

---

## Bucket 5 — Drop (opinion or low-level technique; not scored)

A _different, equally good_ spec may decide these differently or omit them. Putting any of these
at a positive-required tier is the core defect of the old criteria.

- **Path2D** specifically, in zoom-normalized coords.
- **Stable ids as cache keys** (technique).
- The specific **data-normalization** scheme for `max−min > Number.MAX_VALUE`.
- **Canvas stacking** (specific highlight technique).
- **DOM vs. canvas** for crosshair/axes/labels.
- Mark **drawing order**; highlight **border-color defaults**.
- **Band API** specifics (two-series vs. `customBars` triplets).
- **React memoization** internals.
- Specific **rejection of WebGL / OffscreenCanvas-Workers** — see Corrections.
- **CSS variables** specifically as the theming mechanism.
- **Multiple Y-axes**, **image export** (deferred features).

### Possible forbidden mention (should-not)

- Proposing **built-in data-discarding decimation** as a core V0 feature — contradicts the
  prompt's "no decimation, can't misrepresent the data" stance. ⚑ confirm whether to score this
  negatively.

---

## Corrections vs. `tech-criteria.md`

These were `MUST`/`SHOULD` "mention" criteria; each rewards mimicking one interchangeable choice:

| Old criterion                                    | Old tier | New bucket                                           | Reason                                                                      |
| ------------------------------------------------ | -------- | ---------------------------------------------------- | --------------------------------------------------------------------------- |
| Log as a special case of symlog                  | MUST     | D2 (deducible) / Drop the "special-case" framing     | The _need_ is deducible; the implementation framing is opinion.             |
| Path2D cache in zoom-normalized coords           | MUST     | Drop                                                 | Pure technique; a WebGL or direct-draw spec is still valid.                 |
| Stable ids as cache keys                         | MUST     | Drop                                                 | Technique.                                                                  |
| Data normalization for huge ranges               | MUST     | D-ish / Raise (extreme-range handling)               | The capability can be raised; the technique is opinion.                     |
| Shared controller reactive-only, no initial sync | MUST     | **M4 (blind-spot must-ask)**                         | This is a trade-off to surface to the user, not a fact to require.          |
| Independent X per series                         | MUST     | D1 (deducible)                                       | Keep, but as a _decision_ it's forced by the problem, not a fidelity check. |
| WebGL rejected (16-context limit)                | SHOULD   | Drop / at most Raise ("addresses rendering tech")    | A spec that _chooses_ WebGL must not be penalized.                          |
| Canvas stacking                                  | SHOULD   | Raise (highlight-perf strategy) / Drop the specifics | Engage the topic; don't require this technique.                             |

---

## Scoring-skill implication (flagged, not solved here)

The current `technical-evaluation` skill scores presence only (`mentioned & consistent`). It
cannot distinguish **asked** (M-bucket) from **decided** (D-bucket) from
**surfaced-as-alternative** (raise). This partition therefore implies the scoring skill must grow
three different checks, and the M-bucket check has to read the **question transcript**, not the
spec artifact. Out of scope for this draft; noted so it isn't lost.

---

## Appendix — draft thinned prompt (bucket 1, rendered)

Provisional. Goal here is to remove _solution-leak_, not to simulate a messy real user (that's the
separate, still-open N=1 generalization problem). Still cleaner than a true naive user would be.

> I want to build a charting library for ML experiment dashboards (Neptune / Weights & Biases
> style). The shape of the problem:
>
> - A dashboard shows **many charts at once** — easily 100+ loaded and 100+ visible — each
>   tracking one training metric.
> - Each chart has **hundreds of series** (e.g. one per run). Original series are 1M+ points; our
>   backend **pre-aggregates them to ~100k points per chart** before they reach the browser.
> - The main thing users do is eyeball the **pack of series to spot outliers** — runs that
>   diverge. At that density individual lines aren't readable; the shape of the pack is what
>   matters.
> - Users need to see **non-finite values (NaN, ±Inf)** because those flag bugs in a run.
> - Once aggregation hides detail, users **zoom in** to see real values. Zoom and hover-highlight
>   must stay **synchronized across all charts** on the page — matching them by hand is hopeless.
> - Metrics span **many orders of magnitude**, so a log-type scale is essential — but values
>   **aren't all positive**, so a plain log scale won't cover them.
> - Different series cover **different parts of the X axis** (some metrics logged sparsely, some
>   runs crash early), so series don't share one set of X values.
> - It has to be **fast**: at least on par with **uPlot** (our performance bar) and more
>   responsive than Dygraphs. We will **not** rely on decimation that throws away data points —
>   spotting outliers means we can't misrepresent the data.
> - It's for the **web**, **React-based**, with as few runtime dependencies as possible.
>
> Write a specification for this library.
