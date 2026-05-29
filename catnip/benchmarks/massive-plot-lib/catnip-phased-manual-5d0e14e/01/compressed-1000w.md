# PlotLib — Canvas-Based High-Performance Plotting Library

## Purpose

Zero-dep, ESM-only React library: line/point/band charts for ML dashboards with hundreds of
simultaneous charts, pre-aggregated server-side data. Throughput ≥ uPlot; responsiveness ≥ Dygraphs;
no client decimation.

---

## Scale Targets

| Dimension       | Target                              |
| --------------- | ----------------------------------- |
| Points/chart    | ≤ 100k (design); ≤ 1M (degraded)    |
| Visible charts  | 100+ (off-viewport virtualized)     |
| Pre-aggregation | Server-side; client never decimates |

---

## Architecture

**Canvas layers** (identical size, absolutely positioned):

1. **Main** — series paths; redrawn on data change or zoom only.
2. **Highlight** — hover emphasis, zoom rect, markers; cleared each pointer event.
3. **DOM overlay** — axes, crosshair, tooltip anchor; React-rendered.

**Path2D caching** — paths compiled in zoom-normalized coords (`[xMin,xMax]×[yMin,yMax]` →
`[0,1]×[0,1]`); `DOMMatrix` transform applied at draw time. Pan/zoom changes only the matrix; no
path recomputation. Cache key = stable caller-assigned series ID; invalidated on data change or
series add/remove. `IntersectionObserver` clears off-viewport caches eagerly; global LRU
(`MAX_CACHED_PATHS`, default 2 000) catches boundary cases. Off-viewport charts render a
size-preserving placeholder; cached paths retained for instant re-entry.

**DPR/Resize** — `ResizeObserver` updates canvas to `layoutSize × DPR`; raster cap clamps DPR if
pixels > 16 777 216; affected paths invalidated (stroke widths are device-px-absolute).

**Rejected backends:** WebGL (16-context limit; no wide lines/dashes), OffscreenCanvas/Workers (IPC
cost eliminates benefit), SVG (layout degrades at 100k nodes).

---

## Coordinate Systems

Each series has an independent X array; chart X domain defaults to their union (overridable via
controller).

Y domain is per-chart and auto-derived: min/max of y within `xWindow` so out-of-view outliers don't
compress the visible range. Override with `ScaleConfig.min/max`. Recomputed via binary search per
redraw — cost is O(visible density).

**Scales:** `linear` (default); `log` = symlog with `linearThreshold → 0`; `symlog` auto-derives
`threshold = median(|nonzero y|)/100` and `base = 10`. Ticks: 5–8 per axis — nice numbers (linear)
or powers-of-base (symlog). Default label: `Intl.NumberFormat` compact; override via
`ScaleConfig.tickFormat`.

---

## Special Values

`NaN` lifts the pen (`×` marker at baseline); `+Inf`/`−Inf` clamped to top/bottom with ↑/↓ markers.
Per-series IQR outlier detection, computed once at ingestion.

---

## Data Model

```ts
type SeriesData = {
  id: string; // stable cache key
  x: Float64Array; // monotonically increasing, no NaN/Inf
  y: Float64Array; // may contain NaN/±Inf
  yLow?: Float64Array;
  yHigh?: Float64Array; // band (both or neither)
  renderAs?: "line" | "points" | "band"; // default: band if yLow/yHigh, else line
  style?: SeriesStyle;
  highlightOutliers?: boolean;
};

type SeriesStyle = {
  color?: string; // auto from 10-color palette if omitted
  strokeWidth?: number; // device px; default 1.5/0/1 (line/points/band)
  pointRadius?: number; // default 3; opacity?: number; fillOpacity?: number; // 1/0.15
};

type ScaleConfig = {
  type?: "linear" | "log" | "symlog";
  min?: number;
  max?: number;
  linearThreshold?: number;
  base?: number;
  tickFormat?: (v: number) => string;
};

type ControllerState = {
  xWindow: [number, number];
  highlightedSeriesIds: Set<string>;
  crosshairX: number | null;
};
```

`Float64Array` required (zero-copy WASM compatibility; V8 monomorphism). `x` sorted on ingestion if
non-monotone; violations reported via `onError` callback.

---

## Shared Controller

Source of truth for `xWindow`, `highlightedSeriesIds`, `crosshairX`. **Reactive-only**: no
mount-time sync event — charts read state via ref on first render, eliminating async blink storms.
API: `setXWindow`, `setHighlight`, `setCrosshairX`, `subscribe`. Uses `useSyncExternalStore` for
React 18 concurrent-mode batching.

```ts
function useChartController(initial?: Partial<ControllerState>): ChartController;
// Share one instance across <Chart>s to synchronize them.
```

---

## React API

```tsx
<Chart
  series={SeriesData[]} height={number} width={number /* defaults to container */}
  controller={ChartController} xScale={ScaleConfig} yScale={ScaleConfig}
  onSeriesHover={(id: string|null) => void}
  onPointClick={(seriesId: string, index: number) => void}
  className={string} style={CSSProperties}
/>
```

---

## Interaction

**Zoom** — drag (commits on pointer-up) or scroll wheel (rAF-throttled) → writes
`controller.xWindow`. Reset button restores full data domain. Limits: ≥ 2 distinct x values; ≤ full
domain.

**Crosshair** — pointer movement writes `controller.crosshairX`; all linked charts draw a vertical
line and nearest-point circle per series (binary search). Tooltip anchor `<div>` positioned at
nearest point; caller renders content.

**Hover highlight** — within 8 CSS px of a series → `highlightedSeriesIds` updated; others dimmed
via highlight-canvas overlay; no main-canvas redraw.

---

## Performance Constraints

- Main canvas: redraws on data change, zoom/pan, resize only.
- Highlight canvas: ≤ 1 rAF (~16 ms) for 100k pts across all visible charts.
- Path2D compilation: < 50 ms at 100k pts (mid-range 2024 laptop, measured).
- Off-viewport charts: zero render cost after mount.

---

## Environment

React ≥ 18. Chrome 88+, Firefox 78+, Safari 15.4+ (`Path2D`, `DOMMatrix`, `IntersectionObserver`,
`ResizeObserver`). No IE, SSR, or Node.

---

## Risks, Assumptions, Open Questions

**Risks:** (1) float32 precision at extreme zoom — mitigated by ≥ 2-point minimum and [0,1]
normalized paths; (2) render spike when many charts enter viewport simultaneously — schedule via
`requestIdleCallback`; (3) canvas memory at 100+ charts × 2 canvases × high DPR — raster-cap default
needs empirical validation.

**Assumptions:** server pre-aggregates per zoom level; callers maintain stable series IDs.

**Open:** optional Y-window sharing via controller? Correct `MAX_CACHED_PATHS` default (2 000 is
placeholder)?

---

## Out of Scope

SSR; a11y; plugins/theming/animations; bar/pie/categorical; CommonJS; pinch-zoom/swipe; legends;
built-in tooltip UI; Y-axis synchronization.

---

## Exports

```ts
export { Chart, ChartController, useChartController, configure };
export type { SeriesData, SeriesStyle, ScaleConfig, ControllerState, RenderAs };
```
