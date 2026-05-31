# Spec: Fast Canvas-Based Plotting Library for ML Dashboards

## Objective

Build a zero-dependency, ESM-only TypeScript charting library targeting ML training dashboards. The core problem: existing libraries either sacrifice performance (Dygraphs, Recharts) or responsiveness/UX (uPlot's imperative API, static renders). This library targets ≤100k points per chart with 100+ charts simultaneously visible, served from pre-aggregated server-side data, and must match uPlot's render throughput while matching Dygraphs' interactive feel.

Primary chart types: line, point (scatter), band (ribbon between two series). The library ships as a React peer-dep component with a reactive shared controller for cross-chart zoom/highlight synchronization.

---

## Requirements

### Must do

- Render line, point, and band series on a 2D canvas
- Handle ≤100k points per chart as the primary target (configurations: 100 series × 1000 pts, or 1000 series × 100 pts); support up to 1M points with graceful performance degradation
- Accept pre-aggregated data from the server — no client-side decimation
- Support 100+ charts simultaneously loaded and visible (viewport-virtualized)
- Mark NaN and ±Infinity values distinctively (gaps, special glyphs, or colored markers)
- Highlight statistical outliers visually (per-series configurable threshold or IQR-based)
- Synchronized zoom and series highlight across multiple charts via a shared controller
- Log scale and symlog scale; symlog parameters (linear threshold, scale factor) must be auto-derived from the data range — no manual tuning required
- Independent X axis per series within the same chart (series need not share an X domain)
- Stable string IDs on series/datasets used as cache keys for Path2D and transform memos
- Reactive-only shared controller: state changes propagate reactively; no imperative "init sync" call that could cause async blink storms on mount
- Stacked canvas architecture: a main canvas for data paths and a highlight canvas for hover/selection overlays, composited via CSS `z-index`
- DOM layer (plain HTML/SVG) for axes, crosshair line, zoom-rect drag indicator
- DPR-aware rendering: multiply canvas backing-store dimensions by `window.devicePixelRatio`; re-render on DPR change
- ResizeObserver on each chart container; re-layout and re-render on resize
- Respect browser raster size cap (typically 16384×16384 px): clamp canvas pixel dimensions before allocation
- Virtualize off-viewport charts: detach/skip renders for charts scrolled out of view (IntersectionObserver); preserve data and state in memory
- Path2D objects cached in zoom-normalized coordinate space; invalidate only on data change or series ID change, not on pan/zoom
- Data normalization on ingest: replace non-finite values with sentinel, sort by X if unsorted, detect and tag outliers

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
- React as `peerDependency` (≥18); no other runtime dependencies
- Exports: `<Chart>` component, `createController()` factory, TypeScript types
- Build tool: Vite library mode or tsup (assumption: either is acceptable; no bundler opinion baked into spec)

### Component architecture

```
<Chart>
  ├── <div container>          ← ResizeObserver anchor; IntersectionObserver target
  │   ├── <canvas main>        ← data paths (line/point/band); z-index 0
  │   ├── <canvas highlight>   ← hover + selection overlays; z-index 1
  │   └── <div dom-layer>      ← axes (SVG or HTML), crosshair, zoom-rect; z-index 2
```

CSS `position: absolute` stack inside a `position: relative` container. The highlight canvas is transparent everywhere except active overlays, so it can be repainted independently without touching the main canvas.

### Rendering pipeline

1. **Data ingest & normalization** (on prop change, keyed by series stable ID):
   - Scan for NaN/±Inf; replace with a `SENTINEL_NAN` / `SENTINEL_POS_INF` / `SENTINEL_NEG_INF` typed constant
   - If X values are unsorted, sort (X, Y) pairs by X; flag series as `wasSorted`
   - Compute per-series statistics: min, max, p5, p95, IQR; tag outlier indices
   - Memoize normalized data object by series ID

2. **Coordinate transform** (on zoom change or data change):
   - Compute `xToCanvas` and `yToCanvas` linear (or log/symlog) mappings for current viewport
   - Zoom-normalized space: map data coords into `[0, 1]²` at the *full data extent*, then scale to canvas pixels. Path2D is built once in zoom-normalized space; during pan/zoom apply a CSS `transform: scale/translate` on the main canvas until the next idle frame, then re-stroke at pixel resolution (deferred redraw pattern).
   - Actually — simpler and more correct: cache Path2D in **data coordinates** (not pixel), and apply a canvas `setTransform` call per frame. This avoids re-stroking entirely for pan/zoom within the cached data range.

3. **Path2D construction** (invalidated by series ID or data change, not by viewport):
   - For each series, build one `Path2D` in data coordinate space
   - Line series: `moveTo` first valid point, `lineTo` subsequent valid points; lift pen at sentinels
   - Point series: build sub-paths for each point (small arc or rect)
   - Band series: two line paths + closing fill region
   - Outlier points: separate `Path2D` per series, rendered with accent stroke/fill

4. **Frame render** (requestAnimationFrame, batched across all visible charts):
   - `ctx.setTransform(scaleX, 0, 0, scaleY, translateX, translateY)` to map data→pixel
   - `ctx.clearRect(...)` then `ctx.stroke(path2d)` / `ctx.fill(path2d)`
   - NaN sentinel gaps handled by pen-lift during Path2D construction (no per-frame branching)
   - Highlight canvas: cleared and repainted on hover/selection events only

5. **Axes & DOM layer**:
   - Tick positions computed from viewport extent; rendered as absolutely positioned `<div>` or lightweight SVG
   - Crosshair: a vertical `<div>` positioned by mousemove offset
   - Zoom rect: a `<div>` with border shown during drag

### Scale types

- **Linear**: standard affine map
- **Log**: `Math.log10(x)` map; domain must be strictly positive (enforced)
- **Symlog** (log = symlog special case):
  - Formula: `sign(x) * log(1 + |x|/C) / log(1 + 1/C)` where `C` is the linear threshold constant
  - Auto-derive `C`: set `C = max(1e-6, p5_abs)` where `p5_abs` is the 5th percentile of `|x|` values across the visible data range, so the linear region spans values too small to be meaningful on a log scale
  - Log scale is symlog with `C → 0` (equivalently, treat pure log as a degenerate symlog where the linear region is infinitesimal and x > 0 is enforced)

### Shared controller

```ts
interface PlotController {
  // Reactive state (e.g. Zustand store or custom atom)
  xDomain: [number, number]   // current zoom X range
  highlightedX: number | null // crosshair X position in data coords
  selectedSeries: Set<string> // highlighted series IDs

  // Actions
  setXDomain(range: [number, number]): void
  setHighlightedX(x: number | null): void
  toggleSeries(id: string): void
  reset(): void
}
```

- Implemented as a plain reactive store (no Redux, no Context waterfall); each `<Chart>` subscribes via a hook
- Controller created outside React tree: `const ctrl = createController()` passed as a prop
- **No init sync**: charts that mount after the controller already has state pick it up immediately via subscription — no event fires "on mount to sync", eliminating async blink storms where newly mounted charts flash at default zoom before snapping

### Viewport virtualization

- Each `<Chart>` registers an `IntersectionObserver`
- When `intersectionRatio === 0`: skip `requestAnimationFrame` scheduling; optionally detach canvas (set `width=0`) to release GPU raster memory
- When re-entering viewport: re-attach and trigger one render pass
- Data, Path2D cache, and controller subscriptions remain alive regardless of visibility

### Performance invariants (testable)

| Metric | Target |
|--------|--------|
| Initial render, 100k pts, 1 chart | ≤ 16 ms (one frame) |
| Pan/zoom re-render (setTransform path) | ≤ 4 ms |
| 100 charts × 1k pts, all visible, first paint | ≤ 200 ms |
| Memory: Path2D cache size | O(total points), not O(zoom levels) |

---

## Alternative Solutions Considered

### WebGL
Rejected. Hard browser limit of 16 WebGL contexts per page; 100 charts would require context sharing or a single global renderer with complex scene management. WebGL also lacks native support for wide stroked lines (requires geometry shaders or triangle strips) and dashed lines, both needed for chart series styling.

### OffscreenCanvas + Web Workers
Rejected. Transferring 100k-point typed arrays over `postMessage` per frame costs ~2–5 ms serialization overhead even with transferable buffers, which exceeds the render budget for fast pan/zoom. The main thread still blocks on compositing. No meaningful gain for CPU-bound 2D canvas work.

### uPlot directly
uPlot reaches our performance bar but its imperative, non-React API requires manual DOM management, making React integration brittle. It also assumes a single shared X axis across all series and provides no first-class synced-controller abstraction.

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
- Mobile touch gestures (pinch-zoom) — may be added later but not specified

---

## Uncertainty

1. **Path2D + setTransform vs. rebuild on zoom**: The spec proposes caching Path2D in data coords and using `ctx.setTransform` for pan/zoom. This works perfectly for line/band series, but point series rendered as arcs may appear stretched if X and Y scales differ. Mitigation: render points as squares (rects) rather than circles, or accept slight ellipse distortion and re-stroke points separately on zoom settle. This needs a prototype to confirm.

2. **Symlog C auto-derivation correctness**: The `p5_abs` heuristic for `C` may behave poorly when the dataset contains many exact zeros (p5_abs = 0 → C clamped to 1e-6, which may still be wrong). May need a more robust heuristic, e.g., the smallest non-zero absolute value.

3. **100+ chart virtualization memory pressure**: Keeping Path2D objects for 100+ off-viewport charts may accumulate significant memory. A LRU eviction policy for the Path2D cache (keyed by series ID) may be needed; size limit TBD based on profiling.

4. **Independent X per series rendering**: When series have non-overlapping X domains, the shared X axis becomes ambiguous. The spec assumes each series has its own X transform but charts share a single displayed X axis (showing the union domain). This may confuse users. An alternative is per-series axis lanes, which complicates layout significantly.

5. **React version assumptions**: Spec assumes React 18+ concurrent mode. If consumers use React 17, the subscription model (using `useSyncExternalStore` or similar) may need a shim. Assumption: React 18 is the minimum.

6. **raster-cap value**: The 16384 px cap is a heuristic based on common GPU limits. Safari on some devices caps at 4096 px. The implementation should query or detect the actual cap rather than hardcoding.
