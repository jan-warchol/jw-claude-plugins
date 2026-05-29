# massive-plot-lib — Spec contradictions vs. reference

Comparison of the three generated specs (`cc-base/spec-1.md` = Velox Plot, `cc-base/spec-2.md`
= PlotLib, `cc-base/spec-3.md` = Canvas Plot) against the reference
(`reference-spec/full-spec.md`).

Notes on scope:

- **Version staging is excluded.** The generated specs intentionally omit V0/V1/V2 distinctions,
  so a spec including a feature the reference defers to V1/V2 (panning, multiple Y-axes, wheel/pinch
  zoom, off-view clip indicators, image export, locale-aware separators, etc.) is **not** counted as
  a contradiction here.
- **Direct** = the spec states behavior that conflicts with an explicit requirement or statement in
  the reference. **Weaker** = a divergence, a questionable design choice against the reference's
  intent, or a reference requirement left unaddressed.
- Line numbers refer to the reference; `§` refers to the offending spec.

---

## Direct contradictions

### D1. NaN gaps: break the line vs. connect across
Reference (line 327): skip missing points and **connect across** — the line continues through the
gap's neighbors.
- **spec-1** (§5.3): `NaN` = path break (`moveTo` next finite point).
- **spec-2** (§2.1, §6.3): `NaN` breaks the path.
- **spec-3** (§9.1): `NaN` produces a visible gap (path break), arguing explicitly against bridging.

### D2. NaN markers omitted
Reference (lines 22–23, 46–49): markers for non-finite values are **required** (bug-hunting), with
representation ideally configurable (ignore / marker / clipped line).
- **spec-2** (§6.4): *"NaN gap … No additional marker."* — explicitly no NaN marker.
  (spec-1 draws a diamond, spec-3 draws an open circle — both fine.)

### D3. Drawing order: bands painted after lines
Reference (line 101): order is **bands, lines, points**, then the same again for highlighted items.
- **spec-1** (§11): strokes all series paths (step 3), **then** draws band fills (step 4) → bands on
  top of lines.
- **spec-3** (§3.5): render loop strokes series paths, **then** calls `drawBandFill(...)` → bands on
  top of lines.
  (spec-2 §6.5 has this correct: band fills first, then lines, then points.)

### D4. Path2D cached in pixel coordinates (rejects prescribed technique)
Reference (lines 239–240): cache Path2D in **normalized data coordinates bound to the data window**,
so the cache survives chart resize and moderate zoom.
- **spec-2** (§7.4, §7.3, §6.6): *"Paths are built in pixel coordinates for the current viewport"* —
  explicitly accepts a *"cache miss on every new zoom level"* and invalidates all entries on resize.

### D5. Y-axis frozen during X-zoom vs. auto-fit maintained
Reference (line 166): when zooming X, automatic Y fit **should be maintained** (re-fit to visible
data), unless explicitly Y-zoomed.
- **spec-1** (§8.1): *"ML loss curves benefit from a fixed y-axis during x-zoom"* — Y is frozen.
  (spec-2 §13.1 and spec-3 §13.2 both correctly keep Y auto-fit.)

### D6. Rounded SI/compact tick labels violate tick-precision rule
Reference (line 123): tick placement must match the displayed label number — **"No rounding … is
allowed"** (the position must correspond to the printed digits).
- **spec-1** (§9.2): labels like `1.2M`, `3.4B` (SI suffix, 2 sig figs) — the printed value is
  rounded, so the tick no longer matches the label.
- **spec-2** (§14): compact notation `"1.2M"`, `"3.5k"` — same rounding/mismatch.
  (spec-3 does not specify a label format that rounds.)

### D7. Highlight model is single-target, not multi-independent
Reference (line 150): programmatic highlight allowing **multiple** lines/bands/points to be
highlighted **independently**.
- **spec-1** (§6.1): `highlight: Signal<HighlightState>` with `{ seriesId, … }` — one series.
- **spec-2** (§6.1): a single `highlight: Signal<HighlightState>`.
- **spec-3** (§6): controller carries a single `highlightX`.

### D8. Highlight hit-testing tied to defined points, not interpolated
Reference (lines 149, 343): highlighting is **not constrained** to series having a defined point
near the pointer; the target is the **closest interpolated y at the hovered x**.
- **spec-2** (§6.5): draws a marker at the **nearest point** per series and *"skip[s] if delta >
  threshold"* — i.e. constrained to nearby defined points, no interpolation.
- **spec-3** (§10.2): filled dot at the **nearest data point** by X distance — no interpolation.
  (spec-1 §10 also uses a nearest-x search rather than interpolation.)

### D9. No whole-line emphasis redrawn on the highlight canvas
Reference (lines 105, 241): highlighted lines/points/bands are **redrawn in highlighted form on the
top (highlight) canvas** (lines effectively drawn twice).
- **spec-2** (§6.5): explicitly **skips** series emphasis (*"draw dim rect … is too expensive;
  instead skip and only mark nearest"*) — only a point marker is drawn.
- **spec-3** (§10.2): only a nearest-point dot is drawn on the highlight canvas; no line emphasis.
  (spec-1 §10 does redraw the series path segment, so it is closer to the reference here.)

### D10. Log implemented as a separate scale with runtime promotion
Reference (lines 161–164): support log **only as a special case of symlog** — a single code path.
- **spec-3** (§4.2): a distinct base-10 log scale requiring strictly positive data that *"silently
  promotes to symlog"* + `console.warn` when a non-positive value appears. This is a dual path and
  produces a data-dependent shape change (a "log" chart silently gains a linear bridge as soon as
  one non-positive value is present).
  (spec-1 §4.2 and spec-2 §5.2 both route log through symlog as the reference intends.)

---

## Weaker divergences / gaps

### W1. Ranges exceeding `Number.MAX_VALUE` not handled
Reference (lines 109, 247): ranges where `max − min` exceeds `Number.MAX_VALUE` must work, **using
normalization**.
- **spec-1** (§12), **spec-2** (§7.4), **spec-3** (§3.3): all normalize via
  `(x − min)/(max − min)`, which overflows to `Infinity` for such ranges; none address the
  mechanism.

### W2. Path2D cache invalidated on every zoom level
Reference (line 240): the cache should remain valid across **moderate** zoom changes; re-normalize
only on large zoom jumps.
- **spec-3** (§3.3): normalizes to the *view range* and keys the cache on it, so any zoom change
  rebuilds. (Resize-stable, but loses the moderate-zoom reuse that spec-1's pre-zoom normalization
  achieves.)

### W3. Symlog auto-parametrization conflicts with full-range support
Reference (lines 38, 41): symlog should support the **whole float range** with a smart automatic
parameter.
- **spec-1** (§4.2): clamps `C` to `[1e-9, 1]`, so data lying entirely outside that band is
  mishandled.
- **spec-2** (§5.3): places `linthresh` at the geometric midpoint of the data range (`√(v_min·v_max)`),
  putting roughly half the data in the linear region; also internally inconsistent (§5.2 says
  log = symlog with `linthresh = 0`, which divides by zero in the §5.3 linear branch).

### W4. Adaptive Y-axis width and label constraints unaddressed
Reference (lines 118–127): Y-axis width **must be adaptive** to label width; labels must not
overlap, must not overflow, and tick positions must match label precision.
- **spec-1** (§9), **spec-2** (§9, open Q2 leans to a fixed width), **spec-3** (§4.1, only "Wilkinson
  + round numbers"): none specify adaptive Y width or the no-overlap/no-overflow constraints.

### W5. Only one band-definition form supported
Reference (lines 98–100): ideally definable **both** by referencing 2 series **and** as error-band
triplets (Dygraphs `customBars`).
- **spec-1** (§5.1): single-series `yLow`/`yValues` (error-band) only.
- **spec-3** (§8.1): single-series `yLower` (error-band) only.
- **spec-2** (§2.1): two linked series (`band-lower`/`band-upper`) only — the error-band/triplet
  form is absent.

### W6. Input-format handling narrower than reference
Reference (line 305): `number[]`, `Float32Array`, `Float64Array`, and `number[][]` (row-oriented)
are all acceptable; reference even leans toward `Float32Array` internally (line 307).
- **spec-2** (§2.1, §15): rejects `number[]` at the type level (+ runtime `console.warn`) and warns
  on `Float32Array` input — i.e. discourages formats the reference treats as first-class.
- **spec-1** (§5.2), **spec-2**, **spec-3**: none support `number[][]` row-oriented input.
- **spec-1** (§5.2), **spec-2** (§5.2): store `Float64Array` internally (opposite of the reference's
  Float32 lean — minor, reference uses soft language).

### W7. Visual / pixel regression testing weak or absent
Reference (lines 50–55): wants an actual **visual test layer** with diff tooling (ideally
cairo-based, with noise reduction such as quantization / AA-off).
- **spec-3** (§12): uses `jest-canvas-mock` (a mock — no real pixels) + perf tests; no pixel diffing.
- **spec-2** (§16): Playwright/browser screenshots — acceptable under the reference's concession, but
  not the preferred approach and without the noise-reduction steps.
- **spec-1**: no testing section at all.

### W8. Browser support matrix pinned to old versions
Reference (line 392): last two versions of evergreen browsers.
- **spec-1** (open Q7) and **spec-2** (open Q7): Chrome 100 / Firefox 100 / Safari 16 — well behind
  "last two versions."

### W9. Bundle-size target invented
Reference (line 362): explicitly **"No target."**
- **spec-3** (§12): sets a `<30 kB` minified+gzip target.

### W10. Reference V0 behaviors left unaddressed
The following reference requirements are not mentioned by the specs noted (silence, not staging):
- **Empty-data fallback** — render axes with a sensible range, e.g. `[0, 1]` (line 173): spec-1,
  spec-2, spec-3.
- **Zoom-too-close / float-precision guard** (lines 139–142): spec-1, spec-2, spec-3.
- **Canvas allocation-failure verification / reduced-raster fallback** (line 181): spec-1, spec-2
  (spec-3 has a raster cap but no post-allocation verification).
- **Single-value range expansion** (line 107): spec-1, spec-2, spec-3.
- **Reversed-range handling** (line 108): spec-1, spec-2, spec-3.
- **Configurable stroke/dash pattern** (line 96): spec-1, spec-2 (spec-3 supports `dash`).

---

## Cross-cutting patterns

Appearing in **all three** specs (strongest signal of what's being missed in the reference):

- NaN bridging (D1) — all three break the line instead of connecting across.
- Ranges exceeding `Number.MAX_VALUE` (W1) — none implement the required normalization.
- Multi-target / interpolated / whole-line highlight (D7–D9) — all reduce it to single-target,
  defined-point-based highlight.
- Adaptive Y-axis width and detailed label rules (W4) — under-specified everywhere.
