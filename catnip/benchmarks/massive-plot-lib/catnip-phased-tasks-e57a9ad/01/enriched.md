# Spec: Fast Canvas-Based Plotting Library for ML Dashboards

## Objective

Build a zero-dependency, ESM-only TypeScript charting library targeting ML training dashboards. The core problem: existing libraries either sacrifice performance (Dygraphs, Recharts) or responsiveness/UX (uPlot's imperative API, static renders). This library targets ≤100k points per chart with 100+ charts simultaneously visible, served from pre-aggregated server-side data, and must match uPlot's render throughput while matching Dygraphs' interactive feel.

Primary chart types: line, point (scatter), band (ribbon between upper and lower bound series). Ships as a React peer-dep component with a reactive shared controller for cross-chart zoom/highlight synchronization.

---

## Requirements

### Must do

- Render line, point, and band series on a 2D canvas
- Handle ≤100k points per chart as the primary target (configurations: 100 series × 1000 pts, or 1000 series × 100 pts); support up to 1M points with performance above 2 fps (sub-frame render impossible at that scale, but still interactive)
- Accept pre-aggregated data from the server — no client-side decimation
- Support 100+ charts simultaneously loaded and visible (viewport-virtualized)
- Mark NaN values as gaps (pen-lift) and ±Infinity values as special edge markers at the top/bottom of the Y axis
- Highlight statistical outliers visually per series: default IQR×1.5 fence, overridable per series via a `outlierFence` prop
- Synchronized X-domain zoom and crosshair position across multiple charts via a shared controller; Y axes are chart-local and not synchronized (intentional — each chart may measure a different quantity)
- Log scale and symlog scale on either axis; symlog parameters (linear threshold C) must be auto-derived from the data range — no manual tuning required
- Independent X axis per series within the same chart (series need not share an X domain); the chart's displayed X axis shows the union of all series X domains
- Stable string IDs on series used as cache keys for Path2D objects and transform memos
- Reactive-only shared controller: state changes propagate reactively; no imperative "init sync" call
- Stacked canvas architecture: a main canvas for data paths and a highlight canvas for hover/selection overlays, composited via CSS `z-index`
- DOM layer (plain HTML/SVG) for axes, crosshair line, zoom-rect drag indicator
- DPR-aware rendering: multiply canvas backing-store dimensions by `window.devicePixelRatio`; re-render on DPR change
- ResizeObserver on each chart container; re-layout and re-render on resize
- Respect browser raster size cap: clamp canvas pixel dimensions before allocation (Safari caps at 4096 px on some devices; detect actual cap at runtime rather than hardcoding)
- Virtualize off-viewport charts: skip renders and optionally detach canvas for charts scrolled out of view (IntersectionObserver); preserve data and controller subscriptions in memory
- Path2D objects cached in data-coordinate space; reuse across pan/zoom via `ctx.setTransform`; invalidated only on data change or series ID change
- Data normalization on ingest: detect and sentinel NaN/±Inf, sort by X if unsorted, compute per-series statistics and tag outlier indices
- Per-series visual styling (color, line width, point radius, dash pattern) specified as props, not a theming system

### Must not do

- Use WebGL (browser 16-context hard limit; no native wide lines or dashed strokes)
- Use OffscreenCanvas or Web Workers for rendering (IPC serialization cost outweighs parallelism benefit at this data size)
- Perform client-side decimation or downsampling (server is responsible)
- Ship CommonJS output
- Require SSR compatibility
- Implement accessibility features (keyboard navigation, ARIA)
- Support bar, pie, or categorical chart types
- Provide a plugin or theming system
- Include animations or transitions

---

## Solution

### Package shape

- ESM-only TypeScript library; single entry point `index.ts`
- React as `peerDependency` (≥18, uses `useSyncExternalStore`); no other runtime dependencies
- Exports: `<Chart>` component, `createController()` factory, TypeScript types
- Build tool: Vite library mode or tsup (no bundler opinion baked in)

### Data format and `<Chart>` API

```ts
interface SeriesData {
  id: string              // stable cache key
  xs: Float64Array        // X values (may be unsorted; may contain NaN/Inf)
  ys: Float64Array        // Y values, same length as xs
  type: 'line' | 'point' | 'band-lower' | 'band-upper'
  bandId?: string         // pair 'band-lower'+'band-upper' with matching bandId
  color?: string          // CSS color string; default from a built-in palette
  lineWidth?: number      // default 1.5
  pointRadius?: number    // default 3 (point series only)
  dash?: number[]         // default solid
  outlierFence?: number   // IQR multiplier; default 1.5; 0 = disable
  xScale?: 'linear' | 'log' | 'symlog'  // default 'linear'
  yScale?: 'linear' | 'log' | 'symlog'  // default 'linear'
}

interface ChartProps {
  series: SeriesData[]
  controller?: PlotController
  width?: number | string    // CSS value; default '100%'
  height?: number | string   // CSS value; default 300
  xLabel?: string
  yLabel?: string
}
```

`Float64Array` is the required input type. Plain `number[]` would force a copy on normalization; typed arrays allow in-place scanning and avoid GC pressure at 1M-point scale.

A band is formed by pairing one `band-lower` and one `band-upper` series that share the same `bandId`. The fill region is drawn between them; each may have its own X array (independent X). If upper < lower at any point, the fill still draws correctly (no clamp).

### Component architecture

```
<Chart>
  ├── <div container>          ← ResizeObserver + IntersectionObserver anchor
  │   ├── <canvas main>        ← data paths (line/point/band); z-index 0
  │   ├── <canvas highlight>   ← hover + selection overlays; z-index 1
  │   └── <div dom-layer>      ← axes (SVG), crosshair, zoom-rect; z-index 2
```

CSS `position: absolute` stack inside a `position: relative` container. The highlight canvas is transparent everywhere except active overlays, so it can be repainted independently without touching the main canvas.

### Rendering pipeline

1. **Data ingest & normalization** (on prop change, keyed by series stable ID):
   - Scan for NaN/±Inf; store sentinel flags in a parallel `Uint8Array` of the same length (avoid mutating input)
   - If X values are unsorted, sort (X, Y, flags) triples by X ascending
   - Compute per-series statistics: min, max, p5, p95, IQR; tag outlier indices into a `Set<number>`
   - Memoize normalized data object by series ID; skip if ID unchanged and array references unchanged

2. **Coordinate transform** (computed fresh each render from current viewport + series ranges):
   - Map data coords → canvas pixels using a `DOMMatrix`-compatible 2D affine (or symlog) transform
   - For linear/log scales: express as `ctx.setTransform(sx, 0, 0, sy, tx, ty)` where s/t derive from the viewport
   - For symlog: cannot be expressed as a single affine; must project each point individually during Path2D construction (Path2D is then invalidated on viewport change for symlog series — acceptable because symlog is less common)

3. **Path2D construction** (for linear/log: invalidated by data change only; for symlog: also by viewport change):
   - For each series, build one `Path2D` in data coordinate space (linear/log) or canvas-pixel space (symlog)
   - Line: `moveTo` first valid point, `lineTo` subsequent valid points; lift pen at NaN sentinels; draw a small marker (⊥ top or ⊤ bottom) at ±Inf sentinels
   - Point: one `rect(x-r, y-r, 2r, 2r)` per valid point (squares, not arcs, to remain undistorted under non-uniform setTransform scale)
   - Band: draw upper path forward, lower path backward, close — one filled `Path2D` per pair
   - Outliers: a separate `Path2D` per series drawn with accent color on top

4. **Frame render** (via a single global RAF scheduler shared by all visible charts):
   - One `requestAnimationFrame` loop per page, not per chart; charts register/deregister with the scheduler
   - Each visible chart: `ctx.setTransform(...)`, `ctx.clearRect(...)`, `ctx.stroke(path2d)` / `ctx.fill(path2d)`
   - Highlight canvas: cleared and repainted on hover/selection events only (not on every RAF tick)

5. **Axes & DOM layer**:
   - Tick positions: Wilkinson-style or d3-scale-compatible algorithm (nice round numbers); rendered as lightweight SVG `<line>` + `<text>` elements
   - Crosshair: a vertical `<div>` updated on `pointermove`; snaps to nearest X value in data coords
   - Zoom rect: a `<div>` with border shown during pointer drag

### Interaction model

- **Hover**: `pointermove` → update `controller.setHighlightedX(dataX)` → all subscribed charts move crosshair
- **Drag to zoom**: `pointerdown` + `pointermove` → draw zoom rect on DOM layer → `pointerup` → `controller.setXDomain(newRange)`
- **Scroll to zoom**: `wheel` event → zoom in/out centered on cursor X position → `controller.setXDomain(newRange)`
- **Double-click / Escape**: reset to full data extent (`controller.reset()`)
- Pan is not a distinct gesture; users drag-select then re-drag to a neighboring region. (No click-drag-pan to avoid conflict with zoom-rect.)

### Scale types

- **Linear**: standard affine map
- **Log**: `Math.log10(x)`; domain must be strictly positive (enforced; error thrown if data contains ≤0)
- **Symlog**: `sign(x) * log10(1 + |x|/C)` normalized to unit range
  - Auto-derive `C`: smallest non-zero `|x|` value in the series, clamped to `[1e-9, 1]`; this places the linear-to-log transition at the scale of the smallest meaningful value
  - Log is the limit of symlog as C→0 on strictly-positive data; implemented as a separate code path for clarity, not as a degenerate symlog

### Shared controller

```ts
interface PlotController {
  xDomain: [number, number]    // current zoom X range
  highlightedX: number | null  // crosshair X in data coords
  selectedSeries: Set<string>  // highlighted series IDs

  setXDomain(range: [number, number]): void
  setHighlightedX(x: number | null): void
  toggleSeries(id: string): void
  reset(): void
}
```

- Implemented as a plain reactive store (vanilla JS `Set` of listeners); each `<Chart>` subscribes via `useSyncExternalStore`
- Controller created outside React tree: `const ctrl = createController()` passed as prop
- **No init sync**: charts that mount after the controller has state pick it up immediately via subscription — no "on mount" event fires, eliminating async blink storms
- Y-axis domain is **not** in the controller: each chart owns its Y domain independently. This is intentional — different charts display different quantities (loss, accuracy, learning rate) that have no meaningful shared Y scale

### Viewport virtualization

- Each `<Chart>` registers an `IntersectionObserver`
- When `intersectionRatio === 0`: deregister from global RAF scheduler; set canvas `width = 1` to release GPU raster memory without destroying the element
- When re-entering viewport: re-register, restore canvas dimensions, trigger one render pass
- Data, Path2D cache, and controller subscriptions remain alive regardless of visibility

### Performance invariants (testable)

| Metric | Target |
|--------|--------|
| Initial render, 100k pts, 1 chart | ≤ 16 ms (one frame) |
| Pan/zoom re-render (setTransform path, linear scale) | ≤ 4 ms |
| 100 charts × 1k pts, all visible, first paint | ≤ 200 ms |
| 1M pts, 1 chart, initial render | ≤ 500 ms (3+ frames acceptable) |
| Memory: Path2D cache | O(total points), not O(zoom levels) |

---

## Alternative Solutions Considered

### WebGL
Rejected. Hard browser limit of 16 WebGL contexts per page; 100 charts would require context sharing or a single global renderer with complex scene management. Also lacks native wide stroked lines (needs geometry shaders) and dashed lines.

### OffscreenCanvas + Web Workers
Rejected. Transferring 100k-point typed arrays over `postMessage` per frame costs ~2–5 ms even with transferable buffers, which exceeds the render budget for fast pan/zoom. The main thread still blocks on compositing.

### uPlot directly
Reaches the performance bar but its imperative, non-React API requires manual DOM management. Assumes a single shared X axis across all series and provides no first-class synced-controller abstraction.

### Dygraphs directly
Responsive and React-friendly but performance degrades above ~10k pts/series. No Path2D caching; redraws the entire chart on every event.

---

## Out of Scope

- Server-side rendering (SSR / Next.js hydration)
- Accessibility (ARIA roles, keyboard zoom, screen reader labels)
- Plugin or theming system
- Animations and transitions
- Bar, pie, histogram, or categorical chart types
- Client-side data decimation or LOD
- CommonJS output / dual CJS+ESM build
- Mobile touch gestures (pinch-zoom)
- Y-axis synchronization across charts

---

## Uncertainty

1. **Path2D + setTransform for point series**: Point series rendered as squares remain undistorted under non-uniform `setTransform` scale (unlike circles/arcs). This is the chosen mitigation, but it differs from most charting library conventions (circles). Prototype needed to confirm visual acceptability.

2. **Symlog C auto-derivation at zero-heavy data**: Using smallest non-zero `|x|` as C may still misbehave if the dataset is nearly all zeros with one outlier non-zero value — C would be set to that outlier, which is probably wrong. A fallback: if >90% of values are zero, treat the axis as linear.

3. **Path2D LRU eviction**: 100+ off-viewport charts keeping Path2D objects in memory may be significant (rough estimate: 100k pts × 2 series × ~50 bytes/pt ≈ 10 MB per chart, × 100 = 1 GB). A LRU cache with a size limit (e.g., 50 MB total) may be required; exact limit TBD from profiling.

4. **Independent X series + union domain display**: When series have non-overlapping X domains the union axis may be confusing. No mitigation planned; documented as a known UX limitation. Per-series axis lanes would fix it but significantly complicate layout.

5. **Global RAF scheduler coordination**: A single shared RAF loop requires a module-level singleton. This works fine in most apps but may cause issues in micro-frontend environments where multiple instances of the library are loaded. Assumption: single library instance per page.

6. **Symlog on Y axis for Path2D caching**: Symlog paths must be rebuilt on viewport change (can't use setTransform). If symlog Y is common in practice, this could be a performance cliff for pan/zoom. Mitigation: cache the last N viewports' paths. Needs profiling.
