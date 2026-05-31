# Canvas Plotting Library — Spec

## Objective

Build a fast, zero-dependency, ESM-only canvas-based charting library for ML training dashboards. The library renders line, point, and band charts over large pre-aggregated datasets (≤100k pts/chart, sourced from 1M+/series server-side). It supports synchronized zoom/pan across many simultaneous charts, outlier hunting, NaN/±Inf markers, log/symlog scales, and independent X axes per series. React is a peer dependency; no other runtime deps.

**Performance bar:** initial render matches uPlot (no client-side decimation); zoom/pan interaction matches Dygraphs (no jank at 60fps); 100+ charts visible simultaneously without cascading re-renders.

---

## Requirements

### Must do

- Render **line**, **point**, and **band** (area between two series) chart types on HTML Canvas.
- Handle **≤100k points per chart** (e.g. 100 series × 1000 pts, or 1000 series × 100 pts); allow up to **1M points** per chart as a softer limit with degraded-but-functional behavior.
- Support **100+ charts loaded and visible** at the same time.
- **Synchronized zoom and highlight** across charts via a shared reactive controller (subscription model; no init-time synchronization to avoid async blink storms).
- **Pan and zoom**: scroll wheel to zoom; click-drag to pan; shift-drag (or equivalent modifier) to draw a zoom-rect; double-click to reset to full domain.
- **Log scale** and **symlog scale**; log is a special case of symlog (when the linear width parameter → 0); auto-derive symlog threshold from data range.
- **Independent X axis per series**: each series carries its own x-values array; no shared time base required. All series in a chart share a single visible x-domain and a single y-axis (one y-domain per chart).
- **NaN/±Inf markers**: render distinct visual glyphs where data is invalid (gap + dot for NaN; capped arrow for ±Inf).
- **Outlier hunting**: visual support for identifying anomalous points (per-series color emphasis when a value is outside N·σ); σ computed per-series from finite values only.
- **Virtualize off-viewport charts**: use IntersectionObserver; skip rendering and release highlight canvas for invisible charts.
- **DPR-aware rendering**: size canvas backing store to `logical_size × devicePixelRatio`; respect a raster cap (max canvas dimension ~32 768 px) to stay within browser limits.
- **ResizeObserver** integration: reflow canvas on element resize.
- **React integration**: export `<Chart>` component and a shared-controller hook/context; avoid React re-renders on animation-rate updates (use refs + direct canvas calls for zoom/highlight).
- Publish as **ESM-only**.

### Must not do

- Use **WebGL** (browser allows ~16 contexts; wide lines and dashes not natively supported).
- Use **OffscreenCanvas or Web Workers** (IPC serialization cost negates offloading benefit at this data scale).
- Perform **client-side data decimation** (server pre-aggregates; library renders faithfully).
- Require or bundle **React** (peer dep only).
- Ship a **CommonJS** build.

---

## Solution

### Canvas layer stack

Each chart instance owns three stacked layers, all sized identically:

| Layer | Type | Purpose |
|-------|------|---------|
| `main` | `<canvas>` | Stable series geometry; re-drawn only on data/zoom change |
| `highlight` | `<canvas>` | Hover/selection overlay; cleared and redrawn at pointer-event rate |
| `dom` | `<div>` | Axes tick labels, crosshair lines, zoom-rect drag handle, tooltip anchor |

Axes labels are in the DOM layer (not canvas) because DOM text scales correctly with DPR and respects system font rendering; canvas text at high DPR requires manual font size adjustments and produces inferior subpixel rendering.

The `highlight` canvas is released (detached, `width=0`) for off-viewport charts; `main` canvas is preserved so that scrolling back into view is instant.

### Render scheduling

All renders are scheduled through a single `requestAnimationFrame` gate per chart. A chart sets an internal dirty flag when data, zoom, or size changes; the rAF callback checks the flag, clears it, then calls `clearRect` and re-applies the context transform and `stroke(path)` / `fill(path)` calls for all series. If no chart on the page is dirty, no rAF is queued.

Multiple rapid zoom/pan events within a single frame are coalesced: only the controller state at rAF fire time is used. This ensures 60fps interaction regardless of event rate.

### Path2D caching

Series paths are computed in **zoom-normalized coordinates**: x ∈ [0, 1] spanning the full domain, y ∈ [0, 1] spanning the chart's shared y-domain. A single `Path2D` object is stored per series, keyed by `(seriesId, dataVersion)`.

At render time, the canvas context receives a transform that maps `[0,1]²` → pixel space for the current zoom window:

```
scaleX = canvasWidth / (zoomXMax - zoomXMin)
translateX = -zoomXMin * scaleX
scaleY = canvasHeight / (yMax - yMin)   // inverted for canvas coords
```

Path cache is invalidated only when data changes. Zoom/pan never invalidates.

**Cache eviction**: when a chart leaves the viewport, its `Path2D` entries are evicted after a 30-second idle timeout. On re-entry, paths are rebuilt from the cached `Float64Array` data (fast: typically < 5ms for 1k points). The `Float64Array` input arrays are never evicted while the chart instance exists.

### Chart type rendering

**Line**: standard `Path2D` with `moveTo`/`lineTo`; stroked via context transform. Gaps at NaN values (see NaN/±Inf markers).

**Point**: at 100k points, individual `arc()` calls are prohibitively slow (~1ms per 1k calls). Instead, points are rendered by stamping a pre-drawn 1×1 or 3×3 pixel `ImageData` tile at each transformed coordinate, or — for larger markers — by building a Path2D of small rectangles (`rect(x-r, y-r, 2r, 2r)`). The approach is chosen based on marker size: pixel-stamp for radius ≤ 1.5px, Path2D rects otherwise.

**Band**: the fill path traverses y-values forward, then y2-values in reverse, then `closePath()`, yielding a closed polygon. Stroked lines along the top and bottom edges are drawn separately to allow independent stroke/fill styling.

### Shared controller

A plain reactive store (signal/observable — no React state) exposes:

```ts
interface ChartController {
  zoom: { xMin: number; xMax: number };      // normalized [0,1]
  highlight: { x: number } | null;
  subscribe(cb: () => void): () => void;
  setZoom(zoom: Zoom): void;
  setHighlight(x: number | null): void;
}
```

Charts subscribe on mount. On zoom/highlight change, the controller fires subscribers synchronously in the same microtask, eliminating the blink storm that arises from async state propagation (e.g., React setState batching across frames).

**No init-time sync**: charts do not call `setZoom` or `setHighlight` on mount; they read current controller state and render to it. This avoids cascading updates when 100+ charts mount concurrently.

Stable chart/series **string IDs** are required by callers and used as cache keys for Path2D objects and controller subscription bookkeeping.

### Scale system

```
type Scale =
  | { kind: "linear" }
  | { kind: "log"; base?: 10 | Math.E }
  | { kind: "symlog"; threshold?: number }   // threshold auto-derived if omitted
```

`symlog` maps values through `sign(x) × log(1 + |x|/C)` where C is the linear threshold. When not provided, C is auto-derived as `max(|data|) / 1000` (three decades of linear region near zero), making `log` a practical alias for `symlog` with a near-zero C.

### Independent X per series

Each series is typed as:

```ts
interface Series {
  id: string;
  x: Float64Array;   // length N, monotone increasing
  y: Float64Array;   // length N, may contain NaN/±Inf
  kind: "line" | "point" | "band";
  bandY2?: Float64Array;  // only for "band"
  outlierThreshold?: number;  // in σ units; omit to disable
}
```

All series in a chart share a **single visible x-domain** (union of all series x-extents, or an explicit `xDomain` prop) and a **single y-domain** (union of all finite y-extents, or explicit `yDomain`). The zoom normalization maps this shared domain to [0,1].

When axes are shared across series (e.g. same time axis), callers simply pass the same array reference. Axes ticks are computed from the chart-level x-extent.

### Axis tick rendering

Tick positions are computed in data coordinates, then projected to pixel positions via the current zoom transform. Linear ticks use a "nice interval" algorithm (multiples of 1/2/5 × 10^n). Log ticks land on powers of the base. Symlog ticks combine linear ticks near zero with log ticks in the log region.

Tick labels are `<span>` elements absolutely positioned inside the `dom` div. On every zoom update, only the `left`/`top` CSS values are updated (no DOM insertion/removal) by recycling a fixed pool of tick elements.

### NaN/±Inf markers

Before building Path2D, the y-array is scanned for special values:

- **NaN**: path has a `moveTo` gap; a small hollow circle is drawn at the x position on the midline.
- **+Inf**: upward-pointing capped arrow at the top of the plot area.
- **−Inf**: downward-pointing capped arrow at the bottom of the plot area.

Markers are drawn in a separate pass on the `main` canvas after the path stroke, so they are not affected by the transform.

### Outlier support

Per-series, callers may pass `outlierThreshold: number` (in σ units, default off). σ is computed from finite y-values only (NaN/Inf excluded). Points beyond the threshold are rendered with a distinct marker glyph (filled circle) in the `highlight` canvas on the initial render pass, and listed in a callback (`onOutliersFound`) for external UI.

### Data normalization

On ingestion (`setSeries`), the library:
1. Converts input arrays to `Float64Array` if not already.
2. Computes per-series `xMin, xMax, yMin, yMax` (ignoring NaN/Inf for extent computation).
3. Records indices of NaN/Inf values in a compact `Uint32Array` for fast marker rendering.
4. Increments `dataVersion` for cache invalidation.

### Viewport virtualization

A single shared `IntersectionObserver` (one per page) monitors all chart root elements. When a chart enters the viewport, its `highlight` canvas is re-attached and a render is scheduled. When a chart leaves, its `highlight` canvas is detached (DOM removed, backing store freed) and its Path2D cache starts a 30-second eviction timer.

### React integration

```tsx
const controller = createChartController();

<ChartControllerProvider value={controller}>
  <Chart
    id="loss-train"
    series={series}
    xScale={{ kind: "linear" }}
    yScale={{ kind: "symlog" }}
    height={200}
  />
</ChartControllerProvider>
```

- `<Chart>` uses a `useEffect` to mount the canvas engine; subscribes to the controller via `controller.subscribe`.
- Zoom/highlight updates bypass React state entirely — the subscription callback writes directly to the canvas.
- Only structural props (series data, scale config, size) trigger React re-renders, which schedule a full redraw.

### DPR / raster cap

```ts
const dpr = Math.min(window.devicePixelRatio ?? 1, 3);  // cap at 3× to limit memory
const RASTER_CAP = 16384;  // conservative; actual browser max is often 32768
canvas.width  = Math.min(Math.round(cssWidth  * dpr), RASTER_CAP);
canvas.height = Math.min(Math.round(cssHeight * dpr), RASTER_CAP);
```

`ResizeObserver` re-runs this calculation when the element's layout size changes and triggers a full redraw.

---

## Alternative Solutions Considered

### WebGL

**Rejected.** Browsers enforce a hard limit of ~16 simultaneous WebGL contexts; the target of 100+ charts makes this unworkable. Additionally, WebGL lacks native wide lines (>1px) and dashed lines; implementing them requires geometry shaders or CPU-side tessellation, adding significant complexity and still not matching Canvas 2D quality.

### OffscreenCanvas + Web Workers

**Rejected.** Transferring zoom/highlight state, hit-test coordinates, and series updates over `postMessage` introduces serialization and scheduling latency. With 100+ charts, the aggregate IPC cost exceeds the rendering benefit. The main bottleneck (Path2D construction) is mitigated by caching, making offloading unnecessary.

### SVG

Not viable. A single 100k-point polyline in SVG DOM is extremely slow to construct and hit-test. 100 such charts would make the page unresponsive.

### Client-side decimation (LTTB or similar)

**Rejected by design.** The server pre-aggregates data at the appropriate resolution. Client-side decimation would discard outliers that are the primary target of the tool, defeating the purpose.

### Reactive framework (Zustand, Jotai, Valtio) for controller

Rejected in favor of a minimal hand-rolled observable. Pulling in a state library would violate the zero-deps constraint. The controller's API surface is small enough that a simple subscriber set suffices.

---

## Out of Scope

- SSR / server-side rendering
- Accessibility (a11y) — keyboard navigation, screen reader support, ARIA
- Plugin system, theming tokens, CSS custom properties
- Animation / transition effects
- Bar, pie, scatter (non-time-series), categorical charts
- CommonJS / UMD build targets
- Data fetching, WebSocket live streaming
- Legend component (caller responsibility)
- Export to PNG/SVG
- Per-series independent y-axes (dual-axis charts)

---

## Uncertainty

1. **React version floor**: assumed React 18+ (concurrent mode, `useSyncExternalStore`). If React 16/17 support is needed, the controller subscription hook needs a different approach.

2. **"Independent X per series" extent**: assumed to mean series are not required to share x-values, but all series still share one visible x-domain. If truly disjoint x-domains (different time ranges in the same chart) are needed, axes logic and zoom normalization need rethinking.

3. **Outlier hunting UX**: the spec assumes a σ-based threshold with visual markers. If the intended workflow is more interactive (lasso selection, click-to-inspect), the API surface needs expansion.

4. **Tooltip scope**: a minimal crosshair + nearest-point value readout is assumed in scope. A rich multi-series tooltip panel is not. If a richer tooltip is required, it needs scoping.

5. **Symlog auto-derivation heuristic**: the `C = max(|data|) / 1000` heuristic is an assumption. If data has widely varying magnitudes across series, per-series thresholds may be needed.

6. **Raster cap value**: 16 384 px is conservative. Actual browser limits vary (Chrome: 65 536 px, Firefox: ~32 767 px). A runtime detection approach (probe canvas allocation) may be preferable to a hardcoded constant.

7. **`useSyncExternalStore` vs. direct canvas update**: the current design bypasses React entirely for zoom/highlight. If the host app needs React-aware coordination (e.g., Suspense, transitions), the integration model may need revisiting.

8. **Memory budget**: 100 charts × 100 series × 1000 pts × 8 bytes ≈ 80MB for data arrays, which is acceptable. At 1M pts/series the budget rises sharply; the 30-second Path2D eviction on off-viewport charts is the primary mitigation, but the raw data arrays are not evicted — callers must manage their own data lifetime.

9. **Empty / single-point series**: behavior for `length === 0` or `length === 1` series should be defined (skip render, no-op on extent computation).
