# Spec: Fast Canvas-Based Plotting Library for ML Dashboards

## Objective

Build a high-performance, zero-dependency, ESM-only plotting library for ML training dashboards. The library renders line, point, and band charts using the 2D Canvas API (no WebGL, no workers). It is designed for dashboards with 100+ simultaneously visible charts, each drawing up to 100k pre-aggregated data points across many series, with coordinated zoom/highlight across charts, log/symlog scales, and first-class handling of NaN/±Inf outlier markers.

Target performance envelope:
- Match or beat uPlot for raw draw throughput at 100k pts/chart.
- Match or beat Dygraphs for interactive responsiveness (zoom, pan, crosshair updates).

React is a peer dependency; the library exposes React components but ships no React code in the bundle itself.

---

## Requirements

### Must do

- Render **line**, **point** (scatter), and **band** (filled area between two series) chart types on a 2D Canvas.
- Support up to **100k data points per chart** (e.g. 100 series × 1 000 pts, or 1 000 series × 100 pts).
- Remain usable (no crash, degraded perf acceptable) with up to **1M data points per chart**.
- Support **100+ charts visible simultaneously** without degrading the page.
- Support **multiple series per chart**, each with its own independent X axis (series do not need to share the same X values or even the same X domain).
- Provide **synced zoom and crosshair highlight** across an arbitrary subset of charts via a shared controller.
- Support **log scale** (positive values only) and **symlog scale** (all values, including zero and negative); symlog is treated as a special case of log with auto-derived parameters (linear threshold `C` and scale factor `B`).
- Mark **NaN** and **±Infinity** values visually (e.g. gap in line + optional marker symbol at the gap site; ±Inf clipped to axis edge with distinct marker).
- Expose stable **series/chart IDs** that callers provide; these are used as cache keys internally (Path2D cache, zoom-normalized coord cache).
- React component API with props-driven rendering: no imperative init/sync methods exposed to consumers; shared controller is reactive-only (state in, callbacks out).
- Support **DPR-aware rendering** (devicePixelRatio), **ResizeObserver**-driven re-layout, and **raster size capping** (configurable max canvas pixel size to prevent GPU memory exhaustion on very large containers at high DPR).
- **Virtualize off-viewport charts**: charts scrolled outside the viewport should release their canvas pixels (blank or placeholder), re-rendering when scrolled back in.
- **DOM-based overlays** for: crosshair line, zoom-selection rectangle, axis labels and tick marks. Canvas used only for data pixels.
- Cache rendered **Path2D objects** in zoom-normalized coordinates so that re-draws on zoom/pan can reuse paths without recomputing point geometry from scratch (invalidated when data or chart dimensions change).
- Normalize input data arrays internally (typed arrays; copy-on-first-use to avoid mutating caller data).
- No runtime dependencies (zero `node_modules` in the production bundle).
- Ship as ESM only; no CommonJS output.

### Must not do

- Must not decimate (subsample) data — the library must render all provided points.
- Must not use WebGL (browser 16-context limit; no native wide line / dashed line support).
- Must not use OffscreenCanvas or Web Workers for rendering (serialization/IPC cost outweighs gains at this data size).
- Must not perform server-side rendering (Node/SSR environment not supported).
- Must not include accessibility (ARIA, keyboard nav, screen reader) features.
- Must not implement animations, theming systems, or plugin hooks.
- Must not render bar, pie, or categorical chart types.
- Must not ship CommonJS output or require `require()`-style imports.

---

## Solution

### Rendering architecture

Each chart instance manages a **stacked canvas layer model**:

1. **Main canvas** (2D, hardware-accelerated): draws all series paths. Redrawn on zoom/pan/data change.
2. **Highlight canvas** (2D, same dimensions, `position: absolute` on top): draws the hover/crosshair highlight state for the focused series. Redrawn only when hover state changes — avoids full redraw for crosshair movement.
3. **DOM overlay layer** (`position: absolute`, pointer-events none): contains axis ticks/labels (absolutely positioned `<span>` or `<div>` elements), crosshair line (`<div>` with CSS transform), and zoom-rect (`<div>` with CSS border).

The stacking order (bottom to top): main canvas → highlight canvas → DOM overlay.

Canvas elements are sized to `width * DPR × height * DPR` pixels; CSS size is `width × height` px. On resize, `ResizeObserver` fires, layout recomputes, canvases resize, and a full redraw triggers. A `maxRasterPixels` cap (default: `4096 * 4096`) limits canvas allocation; if `width * height * DPR² > cap`, DPR is clamped.

### Path2D caching

Series paths are expensive to recompute for large point counts. The library caches a `Path2D` per series in **zoom-normalized coordinates**: a coordinate space where the full X/Y data range maps to `[0, 1]`. On zoom or pan, the canvas context is transformed (`ctx.setTransform`) to map the visible sub-range of normalized space to canvas pixels — no path recomputation needed.

Cache keys: `(chartId, seriesId, dataVersion)`. `dataVersion` is a monotonic counter incremented on data prop changes. On zoom/pan the transform changes but paths are reused. On data change or canvas resize, paths are invalidated.

Paths are generated with `Float64Array` → typed coordinate buffer → single `Path2D` construction loop. For band charts, the forward pass of the upper series and reverse pass of the lower series are combined into a single closed `Path2D`.

### Data normalization

On first data assignment, input arrays (plain JS arrays or typed arrays) are copied to `Float64Array` (X) and `Float32Array` (Y, sufficient for most float32 training metrics). NaN and ±Infinity are preserved as-is in the data arrays; the rendering pass detects them and:
- NaN: issues a `moveTo` (line gap) and optionally places a small diamond marker DOM element.
- +Infinity: clips Y to the top axis edge; places an upward-arrow marker DOM element.
- -Infinity: clips Y to the bottom axis edge; places a downward-arrow marker DOM element.

### Scale system

Three scale types:
- **Linear**: identity mapping.
- **Log**: `log10(v)` mapping; only positive values valid; a pre-pass warns on non-positive and treats them as NaN.
- **Symlog**: `sign(v) * log10(1 + |v| / C)` where `C` (linear threshold) defaults to `max(|v|) / 1000` (auto-derived from data on each data change). `B` (scale factor) is fixed at 1 and not exposed. Symlog is the only log variant that handles zero and negative values.

Scale type is a per-axis prop (`xScale`, `yScale`). Independent X per series means each series carries its own `xScale` instance; Y scale is shared per chart.

### Shared controller (zoom/highlight sync)

A `PlotController` object holds reactive state:
- `zoomRange: { xMin, xMax } | null` — shared X zoom window (null = full range).
- `highlightX: number | null` — crosshair X position in data coordinates.
- `highlightSeriesId: string | null` — focused series.

Charts subscribe to the controller via React context. The controller exposes no imperative `init()` or `sync()` method — it is purely driven by prop/state updates and emits change callbacks (`onZoomChange`, `onHighlightChange`) that callers wire to their own state. This prevents the "async blink storm" pattern where multiple charts race to initialize sync state on mount.

Zoom interaction: pointer-down + drag on a chart → zoom-rect DOM element tracks the drag → pointer-up triggers `onZoomChange(newRange)`. Pan: hold modifier key + drag → adjusts range proportionally.

### Viewport virtualization

An `IntersectionObserver` (threshold: 0) watches each chart's root DOM element. When a chart leaves the viewport, its canvas pixels are cleared (both canvases set to 0×0 or `display:none`) and the series path cache entries are retained (memory) but the canvas context is released. When the chart enters the viewport, canvases are re-allocated and paths are re-drawn. The virtualization boundary is the scroll container; 100+ charts can exist in the DOM with only the visible subset consuming canvas memory.

### React API sketch

```ts
// Shared controller (create outside render, pass via context)
const controller = usePlotController();

<PlotControllerProvider controller={controller}>
  <Plot
    id="loss-chart"
    width={600}
    height={300}
    series={[
      {
        id: "train-loss",
        x: Float64Array,   // pre-aggregated, server-provided
        y: Float32Array,
        color: "#4f8ef7",
        xScale: "linear",
      },
      {
        id: "val-loss",
        x: Float64Array,
        y: Float32Array,
        color: "#f74f4f",
        xScale: "linear",
      },
    ]}
    yScale="log"
    chartType="line"   // "line" | "point" | "band"
  />
</PlotControllerProvider>
```

`id` on `<Plot>` and each series object is stable and used as the cache key. Changing `id` is equivalent to replacing the series entirely.

### Build / distribution

- Bundled with **Rollup** (or **tsup**) to a single ESM `.js` file + `.d.ts` declarations.
- `peerDependencies`: `react`, `react-dom` (≥ 18).
- `dependencies`: none.
- Tree-shakeable: each chart type importable independently.
- TypeScript source; strict mode.

---

## Alternative solutions considered

### WebGL
Rejected. Browsers limit hardware-accelerated WebGL contexts to ~16 per page. A dashboard with 100+ charts would hit this limit immediately, causing silent fallback to software rendering (worse than 2D canvas). Additionally, WebGL has no native support for wide strokes or dashed lines — both require custom geometry generation, adding significant complexity with no net benefit at our data scale.

### OffscreenCanvas + Web Workers
Rejected. Transferring 100k-point data arrays over `postMessage` to a worker incurs serialization cost that negates the off-main-thread benefit at this data volume. For the target 100k-point draw time budget (~2–5 ms in uPlot on modern hardware), IPC overhead (~0.5–2 ms per transfer) is not acceptable. Path2D objects cannot be transferred (they are not transferable). Keeping rendering on the main thread with an efficient Path2D cache is the better trade-off.

### Decimation / downsampling
Explicitly rejected per requirements. The user's data is already pre-aggregated server-side; the library must render all provided points faithfully to avoid hiding outliers, which is a primary use case.

### SVG rendering
SVG DOM per point at 100k+ scale is unusable (massive memory, slow layout). Rejected without further analysis.

---

## Out of scope

- Server-side rendering (SSR / Node.js environments).
- Accessibility (ARIA roles, keyboard navigation, screen reader support).
- Animations and transitions.
- Plugin / extension system.
- Custom theming API (colors/fonts are passed as props directly; no CSS variable-based theme layer).
- Bar charts, pie charts, categorical axes.
- CommonJS output / `require()` support.
- Automatic data aggregation or decimation (caller is responsible for pre-aggregation).
- Touch / mobile gesture support (pinch-to-zoom) — may be added later.
- Export to PNG/SVG.

---

## Uncertainty

1. **Path2D zoom-normalized cache hit rate**: The design assumes that most re-draws during zoom/pan are served from cache via canvas transform changes. If user workflows involve frequent data updates (e.g. live streaming metrics), cache invalidation may be frequent enough to negate the benefit. An LRU eviction policy (cap total cached paths by memory estimate) may be needed.

2. **Symlog auto-derived `C` parameter**: Auto-deriving `C = max(|v|) / 1000` is a heuristic. For distributions with extreme outliers, this could compress most of the data into a tiny visual range. A smarter heuristic (e.g. percentile-based) or an explicit override prop may be needed.

3. **Virtualization interaction with zoom sync**: When an off-viewport chart re-enters the viewport, it must quickly restore the current zoom state from the controller before painting. The design assumes this is straightforward (read controller state on mount/re-enter), but race conditions with rapid scroll + zoom interactions need testing.

4. **ResizeObserver + 100+ charts performance**: Attaching one ResizeObserver per chart (vs. a single shared observer) may have non-trivial overhead. Should benchmark whether a single shared observer with a WeakMap of callbacks is faster.

5. **Independent X per series and shared zoom**: The zoom controller stores a single `xMin/xMax` window. With independent X domains per series, what does a shared zoom mean? Assumption: the zoom range is in normalized `[0, 1]` space (fraction of each series' own X extent) rather than absolute data coordinates. This needs explicit API design and documentation.

6. **Raster cap behavior**: When `maxRasterPixels` is hit and DPR is clamped, the result is a blurry chart on high-DPR displays. The fallback behavior (warn? silently clamp? show indicator?) should be defined.
