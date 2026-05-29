# Plot library outline

The goal of this project is to create fast, canvas-based plotting library.

This is inspired mainly by my work at Neptune AI where I created a dedicated charting library.
The main inspirations with available source are Dygraphs and uPlot libraries, and the goal
is specifically to surpass them in a number of areas, at least for selected cases.

The library is not intended as a generic go-to charting tool, but rather as a specialized, performance-focused
solution for handling massive data. Therefore a number of concerns may be pushed explicitly on the library user,
such as data decimation and initial axis synchronization. In the long-term vision I'd like to address these issues
by providing some dedicated utils bundled with the library, but I don't intend to make them work out-of-the-box.

## Canonical use case

The main use of the charts in Neptune would be showing many charts (for different ML-training metrics)
with many (hundreds) series each. The original series would be 1M+ points long, aggregated (server-side)
to fit the pixel width of the chart (hard-capped at total of 100k points per chart). Different users
would focus on different details, but one common use was looking for outliers. This is the main reason why
drawing million-points charts even makes sense - although individual lines aren't really visible, you can
see the overall shape and easily spot series that differ from the pack. Some users would also want to look
for non-finite values (Inf, NaN), as these would be indicator of bugs, so markers for these values were
also required, on top of showing the "proper" values. The aggregation means that to get to the bottom of
the data and see actual values, zooming in is required. In order to track multiple metrics together both
the zoom and highlight/crosshair must be synchronized between all the charts, as matching the zoom
of different charts by hand would be extremely tedious and error-prone. Some of the metrics may be
logged only at selected step/X values, and some would end early (e.g. still-running or crashed experiments), so
the subsets of X values may differ between the series. Metrics often span many orders of magnitude, making
the logarithmic scale a necessity. They are still not all positive though, which doesn't play well with logscale;
at Neptune we solved this issue partially by indicating the non-positive values, but symlog scale would be the real
solution.

## Priorities

- Displaying interactive line charts with many (1000+) lines with many (1000+) points each,
- Superior responsiveness and render performance, on par or better than uPlot,
- Built-in support for highlight and zoom,
- Support for linear, logarithmic, and symlog (log + linear hybrid supporting whole float range)[^1] scales, including:
  - Very good scale labeling for most numeric ranges,
  - At least decent handling and scale labeling for every finite numeric data range,
  - Symlog scale parametrization should be automated, with manual override only as a fallback option.
- Support for displaying many charts at once (at least hundreds loaded on the page, with 100+ visible) with
  ability for shared interactions (shared highlight and zoom). The effective per-chart data capacity is expected
  to be reduced when many of them are visible at once, but 100 charts showing 1000 series each, capped at 100k points per
  chart should still be usable.
- Built-in ability to represent non-finite values in the data: NaN and Infinity/-Infinity values should be represented on
  the chart. When displaying logarithmic scale, negative values should also get handled gracefully and with minimal
  information loss. The specific representation is left to be fully determined, ideally it would be configurable between
  ignoring them, showing dedicated markers, and/or edge-clipped line going to ±∞.
- Fully typed TS code with reasonable test coverage, with main focus on unit-testing the utility functions but also a layer
  of visual tests. Canvas is notoriously problematic to test well due to implementation and even hardware details affecting
  the results. I'd like to use something like cairo-based canvas for testing in order to avoid a heavier, browser-based
  solution, but I take into account that running in browser may be the only way to allow visual testing. The idea is
  to make diff testing automated; it will likely require jumping through some hoops to minimize the noise. I expect that
  it will take a while to figure out, but some mixture of color quantization, size reduction and disabling antialiasing should give acceptable results.
- Zero dependencies (apart from React for React component).

[^1]: Symlog (symmetric logarithmic) scale is an extension of logarithmic scale, using `-log(-x)` for negative values and a small linearly-scaled bridge around zero.

## Project stages

There are 3 major milestones I see for this project:

### V0 / Stage 0 / Technical groundwork for priority use cases

At first, I want to have a solid technical groundwork and good support for Neptune-like use case. I don't really care for
the library to be usable for anyone but me at this stage. It doesn't have to support any other cases, the API may be
restricted and potentially cumbersome, any extendability is off the table.

I don't really expect it to be publishable as something that someone would like to use, though for the implemented features
I expect to already have production quality.

### V1 / Stage 1 / Feature completeness for selected cases

This stage is about finishing up the library to be in a publishable state that someone might want to use. The data API
must be in a stable state and support inputs in Dygraph-like and uPlot-like formats. The feature set is still very limited,
but the support for existing features is well polished.

### V2 / Stage 2 / Public library

Extending the library into something well-rounded and with enough versatility that it might be used for various use
cases, more than just the very limited priority scope. Ideally that would include built-in support for multiple kinds
of plots (line/bar/scatter/other?) and at least some level of extendability.

This stage is more of an ambitional goal than an actual plan. I'll be quite happy if the project gets to V1 completion.
However, without at least outlining this long-term direction the vision would be incomplete.

## Detailed scope

Unless labeled otherwise, the features should be included at **V0** stage.

### Features

- For **V0**, I only plan to support charts with lines, points, and bands. That is going to make stuff like
  histograms, stacked charts or scatter plots possible, but I don't plan to support them natively at this stage.
  - Lines are defined by multiple points drawn with a stroke with configurable width, color, and stroke pattern,
  - Points are defined as degenerate lines with just a single point, with separately configurable dot size,
  - Bands are filled areas between 2 series - e.g. to represent error bounds. The exact API to define them is to be
    determined, ideally it would be possible to define them both by referring to 2 series, as well as define them as
    error band for a series (e.g. with triplets like for [Dygraphs' `customBars` option](https://dygraphs.com/1.1.0/options.html#customBars)),
  - Drawing order is: bands, lines, points, then the same again for highlighted stuff. Drawing order between series should be
    deterministic and most likely the order in which they are supplied.
  - Highlighted bands/lines/points get re-drawn on the top with optional border added. For lines and points the default
    border color should match the plot background color. For bands (which are going to be semi-transparent by default)
    the border is going to be the full color with no transparency or limited transparency.
- Any data range defined with finite numbers is supported.
  - Single-value ranges are automatically expanded to include a bit of context,
  - Reversed ranges render in reverse order (to be confirmed; I may change my mind to just make them automatically sorted, or to degenerate them to the starting point),
  - Ranges with `max - min` exceeding `Number.MAX_VALUE` are working correctly (using normalization).
- Decimation/aggregation:
  - **V0**: No support. It's on the user/client to take care of that. The assumption is that performance-concerned
    client would be restricting the data size to fit the display at the source.
  - **V1**: I'd consider adding at least some basic utils for input decimation, but it's low priority. No built-in decimation.
  - **V2**: Final form should have some decent support for processing and aggregating/decimating the data, but most likely just in form of dedicated utils.
  - The canonical use case has data coming from the backend already aggregated to a limited number of points. Providing a decimation/aggregation util
    and examples for how to make it work correctly with the zoom would be actually great, but I want to avoid bloating the core library, especially
    given that almost every JS-based solution will either compromise performance, data accuracy, or both.
- Axis labels on numerical scales correctly working for any range, including extremely small and extremely large ranges.
  "Correctly working" includes:
  - At least 2 labels for each axis (if possible - in edge cases they might not fit within width),
  - No label gets repeated (i.e. at least one digit difference between them); they need enough significant digits to avoid that,
  - Tick placement must match the displayed label number. Essentially, the ticks must be created with precision at which
    the labels are going to be displayed. No rounding (apart from what is required by binary floats not quite matching the decimal numbers) is allowed. In edge cases the precision may be reduced if it doesn't visibly change the tick placement (i.e. the difference is significantly lower than 1px).
  - No labels overlap,
  - No labels overflow outside the chart,
  - Labels are aligned to nice decimal values when feasible,
  - In order to meet these requirements, the Y-axis width must be adaptive to the required labels width. X-axis labels
    are expected to have fixed height, although allowing angled/vertical labels on X axis would be a great extension at **V2**.
  - Locale support and possible a11y for labels are **V2** concern.
- **V1**/**V2** Possibility to inject labels for specific values as override (e.g. to highlight first X value) while keeping the above constraints for good labels.
- Number formatting on axes (precision, scientific notation threshold for very large/small numbers) is determined automatically from the chosen tick values. Per-axis formatter override is a **V1** concern. Locale-aware separators are a **V2** concern (covered by the locale support point above).
- Time-based scales are treated kind of best-effort at **V0** stage and may have sub-par ticking and labeling, including:
  repeating the same label, missing labels, overlapping labels for edge cases. At **V1** time-based series should get
  proper support, although I still expect to give them less attention and some improvements may still be deferred till **V2**.
  - Date as input type should be allowed for time-based X values, but it may be deferred to **V1** or even **V2**, with number (timestamp) as the basic input.
    TBD: Timezone support. For **V0** I'm going to assume just using the browser's timezone.
- Integrated zoom with good performance (looking at you, Dygraphs).
  - **V1**/**V2** Preferably support for pinch zoom and pan on touchscreens.
  - Zoom needs to be aware of floating-point precision and prevent zooming in too close (especially to single-value ranges). At **V0** silent failure
    or slightly changing the range in such case is just fine, at **V1**/**V2** a more polished solution would be welcome:
    - Zoom rectangle should show the actual zoom range, not the mouse move range,
    - Zooming in too close should be forbidden with some form of explicit message.
  - Partial zoom out (like x2) instead of just zoom reset would be nice as an option, but it's not trivial to implement correctly (especially in conjunction
    with the shared zoom), hence it's not going to be present at **V0** and most likely it will be left as nice-to-have for late **V2** to pick up.
  - It's not yet quite clear to me where the zoom state should live. Most likely it will be a state or controller delivered by React context,
    with dedicated provider component being part of the library. A prop override is likely to be available on top of that.
- Integrated line and point highlights:
  - Highlight with mouse/pointer,
  - Highlighting lines is not constrained by the line having defined points close to the pointer,
  - Programmatic highlight allowing to highlight multiple lines/bands/points independently.
  - Integrated tooltip showing hovered values or all values at hovered X. I don't have clarity yet how far I want to
    develop that as built-in feature or whether it should stay very basic and only get developed further as a plugin
    (in **V2** stage). An always-on display for hovered value might also be an alternative. It may be implemented as
    a separate component that is connected to the plot by the shared state context/controller.
- At least rudimentary support for shared highlight and zoom, preferably a dedicated shared highlight and zoom controller.
  - Shared zoom is designed for handling user-initiated zoom, and doesn't cover sharing the X/Y axis ranges on load. If X/Y axes should be
    shared at initial display, this needs to be handled by client and passed to the charts in props (or _maybe_ passed directly to the controller as initial
    state). The charts can't figure out correct shared ranges on their own without sacrificing performance and UX (data loading asynchronously would result
    in massive re-renders wave, resulting both in chocking the CPU/GPU and interface blinking - that's completely unacceptable).
- Some sort of legend. This is a large topic, so for first iteration it's likely to be a bit of an afterthought. Switching series visibility may be implemented eventually, but is not expected at **V0**.
- Log and symlog scale:
  - Supporting logarithmic scale comes with a lot of fiddling with the values to correctly handle non-positive coords.
    This gets pretty tedious, and I consider supporting log scale only as a special case of symlog scale (which might make
    it behave slightly different to usual log scale display wrt. non-positive inputs).
  - Log and symlog scales don't need to support time scales.
- Automatic fit to data on both X and Y scales, with padding size defined in pixels or in relation to chart size. When zoomed in, the automatic fit on Y axis should be maintained, unless explicitly zoomed in on Y axis. Auto zoom should never show range exceeding last Y axis zoom (i.e. it can only narrow it down).
- Minimal built-in palette for series colors - the plot should be usable with only minimal configuration (i.e. it
  should figure out _some_ colors), but the expectation is that beyond very basic use cases the users will provide the colors.
- Axes and tick-based grid should be displayed by default. It would be good to have uPlot-style crosshair available as an option, or an X-value line (Neptune-style).
- Robust handling of bad inputs:
  - No type-correct configuration should result in a crash, especially non-finite numbers should be handled gracefully. The exact behavior for inconsistent inputs is unspecified.
  - Clearly malformed inputs should result in exceptions, preferably with a descriptive error message, though details are to be determined. The assumption is that it's unlikely to have _very_ wrong inputs outside of development environment. I may want to revise that in the future if the library gets any actual usage.
  - Empty data (no series, or all series with no finite points): render axes with a sensible fallback range (e.g. `[0, 1]`) and no series. No built-in loading state — that's the consumer's responsibility.
- Simple callbacks for handling built-in interactions (hover, zoom, zoom reset, pass-through for regular events). Clicking on the series is unlikely to get special handling, and rather rely on the highlight, but may get a dedicated callback that would return the currently highlighted series.
- Callbacks should provide some object with utils for coords conversions (data ↔ screen)
- In React flavor, there may be a more imperative interface exposed optionally through a ref. I don't have it clarified
  yet and it's subject to change.
- Robust canvas size handling:
  - automatic size adjustment to devicePixelRatio,
  - max canvas size cap (to preemptively avoid hitting max canvas size),
  - canvas drawing verification to ensure successful allocation (forcing reduced raster size in case of a failure, on an assumption that size limit was the reason).
- Support for multiple Y-axes might happen at **V1** or **V2**.
- Some sort of virtualization support is necessary to keep off-screen plots from messing up the performance. This seems simple enough to be included in **V0**, but might get deferred to **V1**.
- I'd like to have some support for image exports. I'm not sure yet at which stage I'd want to add it, most likely early **V2**.
- Streaming data support and optimization is not my focus. Some support is likely to happen in **V1**, but I don't plan to optimize performance for this specific use case.
- Explicitly not supported until **V2**:
  - Full theme configuration,
  - Plugins,
  - Customized interactions,
  - Displaying any extra stuff not mentioned above (e.g. extra markers),
  - Range selection,
  - Panning,
  - Any sort of animations. Any animations are unlikely to happen due to performance constraints, but actually it would be nice to make them available for less demanding charts.
  - Bar charts, pie charts, other kinds of charts (though some minimal chart shape customization may happen at **V1**),
  - Categorical X axis (like in bar chart, with strings as labels for each discrete value). These don't really make sense for line charts.
  - Accessibility.
- Out of scope:
  - SSR,
  - Legacy browsers support,
  - Accessibility beyond something very basic at **V2**,
  - Auto synchronization of axes between charts on initial load; synchronized zoom and highlight are only reactive to user interactions (maybe also to programmatic inputs - TBD).

### Performance

- uPlot is the main contender here and benchmark here, as it's significantly faster than Dygraphs, which contains a bunch of severe bottlenecks, though there are some cases where Dygraphs may be better. The goal is to be better or at least on par in:
  - initial drawing,
  - redrawing the chart,
  - highlighting points and lines.

  Note: uPlot has built-in support for decimation, which might give it an edge in some cases. This is sort of cheating though, as it misrepresents the user data, and I'm not considering uPlot with decimation as part of the benchmark.

- Specific performance goals are to be determined. Right now it's more about figuring out what is possible.
- More concrete performance testing scenarios I have in mind:
  - Small scale (expecting ≫60 FPS highlight/resize/interactions):
    - 1 large (fullscreen) chart with 20 lines x 1000 points each,
    - 10 smaller charts with 20 lines x 1000 points each,
    - Each of the above with added more loaded charts outside the viewport.
  - Large scale (expecting >30 FPS highlight/resize/interactions):
    - 1 large (fullscreen) chart with 1000 lines x 100 points each,
    - 1 large (fullscreen) chart with 1000 lines x 1000 points each,
    - 10 smaller charts with 1000 lines x 100 points each.
    - 10 smaller charts with 100 lines x 1000 points each.
    - 10 smaller charts with 100 lines x 300 points each.
    - 100 smaller charts with 100 lines x 300 points each.
    - Each of the above with added more loaded charts outside the viewport.
- Apart from FPS, the initial render time may be a significant issue. I don't have clarity on it yet; I need to see what kind of performance we get with actual implementation and iterate from there. uPlot's performance is going to be a reference, however I'm willing to trade a little bit of extra first render time for more responsive interactions.
- For practical reasons, I'm most likely going to use my own laptop as a reference. I might defer to an older laptop
  in order to get a more practical baseline for average user. However, Neptune was written for users with beefy machines
  and so the most natural approach right now is more along the lines of "let's get everything this machine can get us"
  rather than looking at worst case scenario.
- I'm not quite sure yet how to load the data for the charts during the tests. Generating it on the fly in JS is way too slow,
  so some sort of ready to use data is going to be necessary.

### Specific technical solutions

- Path2D caching to optimize drawing and redraws. Although cache may not be always useful (if the data is changing a lot, especially with mutable input interface), my experience shows that building Path2D and rendering it has (sometimes much - especially in FF) better performance than calling canvas functions directly, even if the path is not reused.
  - Path cache should aim to be stored in data coords normalized roughly to the displayed data window. Normalization should
    be bound to configured data window and zoom rather than exact displayed range (which is affected by margins, and may
    change with any small chart resize). If done right, it's going to keep the cached values valid for any chart resize,
    as well as moderate zoom changes. Only large zoom changes (100x? 1000x? 100000x? not quite sure yet) warrant re-evaluating the normalization.
- Canvas stacking. For interactive highlights the plots should use secondary canvas displayed on top of the main canvas with the plot. This implies that highlighted lines will be effectively drawn twice - once as regular lines, and the second one in highlighted form on top of that.
  - This approach relies on an assumption that the number of highlighted lines is far smaller than the number of all lines
    to provide significant performance boost. In edge cases where this is not correct, the highlighting may get quite costly,
    as it will require essentially redrawing the whole chart. There isn't really a way around it, so that's the deal we have
    to take.
- Separate DOM elements for more interactive stuff like crosshair or zoom rectangle, possibly also for axes and axis labels.
- Data normalization. In order to be able to display any float subrange we may need to scale the coords by a factor exceeding what float64 can express. Data normalization should help with handling that.

### Technical solutions that might be considered (but probably won't cut it)

- OffscreenCanvas / Worker rendering: Worth considering, but not aimed for in **V0**. The main concern is data transfer:
  if transferring the data would require extra rewrite of it, it almost certainly defeats the purpose. Offscreen canvas
  would then require transferring the data to the actual canvas element, which is also not free. There is surely some potential, but it's far from obvious how much can be gained, while added complexity is quite substantial.
- I take into account a possibility of writing a WebGL-based fork of the library. However, my earlier experimentation
  suggests that potential performance benefits are minor at best and come with a hefty price of dealing with a shared
  WebGL context (required when working with many visible plots) and a lot of low-level fiddling with rendering. This is in
  large part driven by the fact that only 1 px lines are supported natively by WebGL, and wider lines must be rendered as
  polygons. Stroke patterns are also not supported by WebGL natively and are very hard to render efficiently. If this fork
  happens, it will be more likely as exploration and for fun than as a serious technical alternative.

### Interface flexibility

- It would be perfect to support both Dygraph-like (row oriented) and uPlot-like (column oriented, X values as one of the series) data formats, but that's an optional goal.
- Allow giving each series independent X values. Both Dygraphs and uPlot are rigid about all series sharing
  the X values. This can be extremely wasteful when working with series that span different parts of X axis
  or have different point alignment, and it's pretty inconvenient to work with within the library itself.
  - This may look like a huge divergence from uPlot/Dygraph on technical side, but it actually isn't. Both of these libraries parse the data and keep it as independent points internally - the shared X values are just quirk of the interface.

### React compatibility

- I intend to make the library play nicely with React and React component being the main (or only) interface to use it.
- Preferably the library is going to have inner framework-agnostic implementation with React-style (memo) cache and a React wrapper, while also providing a more imperative interface more similar to uPlot's and/or Dygraphs'.

      I believe writing this kind of library in style of React's functional component is a very clean and efficient choice,
      so even if V0 will be fully React-based, conversion to framework-agnostic implementation should be relatively
      straightforward and mostly boil down to providing the memo implementation and interface layer.

      Providing the imperative interface that would allow mutable inputs is going to be a slightly bigger challenge with
      this approach. However, I believe that mixing the memo approach with right cache invalidation keys should be just
      enough to make it work. In case this turns out to be false, I'm going to prioritise the declarative interface and
      either slash the mutable inputs completely, or make them available only with performance penalty - this is not the
      core feature.

### Memoization vs data updates

- Barebone React-style memoization is not going to work great for some cases, like if the series are added to plot or removed
  from it. A more capable approach that would match larger pieces of data (e.g. arrays representing data series) instead of just
  the whole thing are going to be necessary.
- Series are going to be identified by ids, which is likely going to be helpful, as cache can rely on the ids as a reference.

## Questions and answers

Some clarifications.

### Series count and point count target

**Q:** The V0 priority of "1000+ lines with 1000+ points each" implies 1M+ points in a single chart. Is that literal, or is the realistic V0 target smaller?

**A:** Both modes are supported, though not necessarily fully at the same time. The main benchmark is **100k points per chart**, which should work both for 100+ series with 1000+ points each _and_ for 1000+ series with 100+ points each. A 1M-point chart should also work reasonably well.

### Input data representation

**Q:** What types are accepted for series data?

**A:** `number[]`, `Float64Array`, `Float32Array`, and `number[][]` (for Dygraph-like row-oriented input) are all acceptable interface formats. The only hard requirement is random access — the library will iterate over the data multiple times, so generators/lazy iterables are out of scope.

Internally the library is likely to copy the input into its own format (most likely TypedArrays). uPlot may keep the raw input all the way through; Dygraphs rewrites it, and that's the path I'm leaning toward as well. The internal format may already be normalized (see "Data normalization" under technical solutions), in which case `Float32Array` should be sufficient even when the original input is `Float64Array`.

**V0** does not fix the data API. The listed types describe a likely surface, but both the surface and the internal representation may shift during performance work; stabilization is a **V1** concern.

### Core / React architecture

**Q:** How should the framework-agnostic core relate to the React wrapper?

**A:** Declarative core with internal caching/diffing. The React wrapper is thin and just forwards props. Trade-off: cleaner React story, but exposing a clean imperative API to non-React users will be harder and is not a V0 priority.

### Streaming / append updates

**Q:** Real-time / append-only data updates interact with the Path2D caching strategy. What's the V0 plan?

**A:** Full redraws on any data change at V0. Streaming-specific incremental Path2D updates are a **V1**/**V2** concern. Live-training-style charts will still work; they just won't get the dedicated optimization yet.

### Missing values (null / NaN)

**Q:** How are gaps within a series rendered?

**A:** Skip missing points and connect across — the line continues through the neighbors of the gap. Matches one of uPlot's modes; configurable per-series behavior is a possible later refinement. In case of bands, each edge of the band is drawn
independently, so inconsistencies between x values are nonconsequential. If the band ends are inconsistent, the outstanding
part of longer series should be ignored. This may require some interpolation of the longer series at the point where the
shorter series start, or only starting/ending at a common x value; I don't have a strong opinion on that yet.

### Out of order values/input sorting

**Q:** Do the inputs need to be sorted? What happens if they are not?

**A:** For the sake of performance and simplicity I'm going to assume that inputs are sorted, and leave the behavior for
out-of-order inputs unspecified. In the future (**V2**?) I'm going to consider tweaking this approach.

### Hit-testing for highlights

**Q:** Highlights aren't constrained to defined points. How is the line/segment under the pointer determined?

**A:** By the closest interpolated `y` value at hovered `x`; if no series has data at the hovered x, fall back to closest `x` with any series present.

### Accessibility

**Q:** What's the a11y plan?

**A:** Out of scope at least until **V2**. Canvas charts are notoriously hard for accessibility. I'd like
to make it at least somewhat a11y-friendly eventually, but it's at the bottom of priority list.

### Resize and devicePixelRatio

**Q:** How does the chart respond to container resize and devicePixelRatio changes?

**A:** Auto by default — the library subscribes to `ResizeObserver` and DPR changes and redraws. Consumers can opt out and drive resize imperatively.

### Bundle size

**Q:** Is there a bundle-size target for V0/V1?

**A:** No target. Correctness and performance come first. Given no dependencies, the bundle size should be rather modest.
If it becomes an issue, cutting the library into some pieces to support tree-shaking better would be a likely approach
to the problem - I don't have plans to address the bundle size directly.

### Build / package format

**Q:** What's the published package format?

**A:** ESM-only, with TypeScript declarations. React is a peer dependency. CommonJS output is not planned.

### Theming and styling

**Q:** How can chart appearance (colors, fonts, axes, grid) be customized?

**A:** Minimal hardcoded styling at V0 — just enough to look reasonable. Full theming story (CSS variables, themes, etc.) is a **V1**/**V2** concern. Basing general styling on CSS variables (with JS config only available as override or not at all) would be preferable, as they can seamlessly support themes (light/dark) and different screen sizes.

### Symlog scale parametrization

**Q:** Symlog scale requires parametrization that significantly affects what it looks like (the parameters being
the size of the linear bridge in data coords and its visible size on the plot). How symlog scale will be parametrized?

**A:** Libraries providing symlog scale implementation usually require giving them the parameters. However, my belief is that good
parameters should be possible to determine from the data and that a smart automatic default should be sufficient for
almost all use cases. This can be sensitive to the exact data values though, so manual parametrization needs to still be available,
so that more consistent results can be achieved if necessary.

### SSR and browser support

**Q:** What's the runtime / browser support matrix?

**A:** Modern evergreen browsers only (Chrome, Firefox, Safari, Edge — last two versions). Browser-only; no SSR support. The React wrapper is a no-op on the server, and consumers using Next.js wrap with dynamic import or `'use client'`.

### WebGL

**Q:** Isn't WebGL the way to go to get max performance?

**A:** Not really, there are severe caveats to using WebGL that hinder its performance, the most notorious being the limit
of open WebGL contexts (just 16 per _domain_ in Chrome), meaning that WebGL context must be shared and the result redrawn
into separate Canvas elements (or there's [the trick with drawing a single fixed canvas](https://threejs.org/examples/?q=multiple#webgl_multiple_elements), but it has different issues).

### OffscreenCanvas / Worker rendering

**Q:** Why not use Web Workers to parallelize the work of drawing multiple canvases?

**A:** We might try it. However, the Worker communication can be quite costly (transferring TypedArrays is the only quick way to transfer large data to/from the worker) so this approach has severe limitations.
