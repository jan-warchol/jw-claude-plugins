# Contradictions with the reference full-spec

Each entry states the reference rule, then lists every evaluated spec (01 / 02 / 03)
that contradicts it. Differences that are purely about V0/V1/V2 feature staging are
excluded, since the evaluated specs intentionally omit version distinctions.

---

## 1. Input data types — rejects formats the reference explicitly accepts

Reference (Q&A "Input data representation", lines 303–307): `number[]`, `Float64Array`,
`Float32Array`, **and** `number[][]` (Dygraph-style row-oriented) "are all acceptable
interface formats." Internally `Float32Array` should suffice even for `Float64Array` input.

- **01** — "`Float64Array` is required (not `number[]`)" (line 219).
- **02** — "typed arrays required; no JS number arrays" (line 53).
- **03** — "Callers using plain `number[]` must convert; the library does not accept plain arrays" (line 417).

## 2. NaN / missing-value line behavior — breaks the line vs. connect-across default

Reference (Q&A "Missing values", lines 324–330): default is "Skip missing points and connect
across — the line continues through the neighbors of the gap." (Markers for non-finite values
are still wanted, and the representation should be configurable — ignore / marker / edge-clipped
to ±∞, lines 46–49 — but the line itself should connect across by default.)

- **01** — "NaN — breaks the path (lifts the pen) so adjacent segments are not connected" (line 166).
- **02** — "`NaN` | Gap (line break)" (line 105).
- **03** — "NaN in `y`: rendered as a visible gap in line charts" (line 56).

## 3. Path2D cache invalidated on resize

Reference (lines 238–240): normalized paths should "keep the cached values valid for any chart
resize"; only *large* zoom changes (100×–100000×) warrant re-normalization. Stroke width is
applied at stroke time, so resize should not bust the geometry cache.

- **01** — on resize, "All cached `Path2D` entries for the affected chart are invalidated" (lines 93–94).
- **02** — "DPR changes... trigger... Path2D cache flush" (line 224).
- **03** — on resize, "all cached paths for this chart are evicted" (line 245).

## 4. Band edges forced to share identical X arrays

Reference (Q&A "Missing values", lines 327–330): band edges may have *inconsistent* X values;
the outstanding part of the longer series is ignored or interpolated. Identical X is not required.

- **02** — mismatched band X "are a usage error and will render incorrectly" (lines 30–32).
- **03** — `band-lo`/`band-hi` "must have the same `x` array"; otherwise the band is not rendered (lines 50–51).

## 5. Path normalization / cache key defeats reuse across moderate zoom

Reference (lines 238–240): normalization should be bound to the configured data window/zoom so
moderate zoom changes reuse cached paths; only very large zoom warrants rebuilding.

- **02** — cache keyed on `zoomLevel` quantized to "128 levels per decade," rebuilt on crossing a
  level boundary (lines 144–146) — re-normalizes on small zoom changes.
- **03** — paths normalized to "the series' local extent" and keyed on exact
  `(xMin, xMax, yMin, yMax)` (lines 206–208) — any zoom change is a cache miss/rebuild.

## 6. Built-in automatic decimation in the core render path

Reference (lines 110–117): the library does not decimate; aggregation is the caller's job, and any
future support should be optional, dedicated utils, never automatic in the core ("I want to avoid
bloating the core library"). The whole point is to not silently misrepresent user data.

- **03** — applies an automatic min/max envelope decimation pass during Path2D construction
  "when the chart pixel width is known and the series has more points than pixels" (lines 64–71),
  and bakes `decimationBucketCount` into the cache key (lines 208–214).

## 7. Built-in tooltip dropped

Reference (line 151): an "Integrated tooltip showing hovered values or all values at hovered X" is
wanted (at minimum a basic built-in one).

- **01** — lists "Tooltip content" as out of scope; only positions an anchor `<div>` and makes the
  caller render all content (lines 416–417).

## 8. Automatic statistical outlier detection — invented feature

Reference: users spot outliers *visually*; the only required value-flagging is non-finite markers
(lines 19–23, 46–49). There is no automatic statistical (IQR/percentile) outlier feature anywhere.

- **01** — adds IQR-based outlier highlighting via a `highlightOutliers` flag (lines 172–174).
- **02** — adds percentile-based (1st/99th) outlier marking with hover rings (lines 113–122).

## 9. Internal inconsistency: NaN gap vs. min/max replacement (spec 03)

Independent of the reference, spec 03 contradicts itself: normalization "Replace flagged
[NaN/Inf] values... with the series' local min/max (for path continuity)" (lines 232–233)
— i.e. connect-across — while the chart-types section says NaN renders "as a visible gap"
(line 56). The connect-across half actually matches the reference; the gap half does not.

---

## Minor / omissions (not hard contradictions)

- **Canvas allocation verification missing (01, 02, 03).** Reference wants "canvas drawing
  verification to ensure successful allocation (forcing reduced raster size in case of a failure)"
  (lines 180–181). All three implement only a static raster cap, not the draw-verification fallback.
- **Auto-fit Y narrowing nuance (01, 02, 03).** Reference: auto-fit on zoom "can only narrow it
  down" and "never show range exceeding last Y axis zoom" (line 166). All three recompute Y from the
  visible window from scratch, which can re-widen.
- **Malformed-input handling (01, 02).** Reference wants clearly malformed inputs to throw with
  descriptive messages (line 172). 01 uses an `onError` callback and never throws; 02 silently
  renders out-of-order data incorrectly. (Reference marks exact details TBD.)
