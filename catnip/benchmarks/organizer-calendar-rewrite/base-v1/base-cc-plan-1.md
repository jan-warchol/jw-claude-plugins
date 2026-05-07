# Plan: Calendar and Time-Based Planning Features

## Overview

Port the calendar/scheduling system from `old-app` to `new-app`. The old app's **TimeBoard** lets users schedule tasks to calendar periods (day, week, month) or to a freeform backlog, then view them in a multi-column timeline. The new app should reproduce this behaviour using its cleaner architecture.

Data format compatibility with the old app is **not required**.

---

## Understanding of the Old App's Features

### What Exists

- **`plannedFor` field** on tasks: `{ parentClass: 'day'|'week'|'month'|'list', parentKey: ISO-date-or-listId, seq: fractional-index }`
- **TimeBoard view**: multi-column timeline with Days / Weeks / Months / Backlog panels; configurable via localStorage
- **Section navigation**: "Show more" / "Show previous" controls that progressively double the visible window; auto-expands past if there are overdue tasks
- **Empty section collapsing**: sections with no tasks are hidden but a counter shows how many are collapsed
- **Quick-schedule menu** on each task: Today, Tomorrow, This week, Next week, This month, Unplanned, Other date…
- **Custom date dialog**: buttons for "in 2 / 3 weeks", "next month", "in 2 months", plus a date picker
- **Bulk scheduling**: same options when multiple tasks are selected
- **Date chip on task card**: compact badge showing the scheduled period in relative terms (Today, Tomorrow, This week, etc.)
- **Repeating tasks**: `repeat: { increment, unit }` field; auto-schedules next occurrence on completion
- **"Active pending" tracking**: expands past sections automatically when overdue tasks exist

### What to Leave Out (for Now)

- Google Calendar event sync
- Multi-team / multi-DB backlog splitting
- The legacy `showInbox` / `notatki` special lists
- i18n (`$gettext`) — use plain English strings

---

## Architecture Design

### Key Design Decision: `plannedFor` as a Standard Relation

The new app models all item relationships through its `Relation` abstraction. The cleanest fit for "schedule a task to a date" is to add a `builtin.plannedFor` relation whose **parent IDs are synthetic date strings** rather than real stored documents.

**Synthetic parent ID format:**

| Granularity | Parent ID pattern | Example |
|-------------|-------------------|---------|
| day | `day:YYYY-MM-DD` | `day:2026-05-07` |
| week | `week:YYYY-MM-DD` (ISO week start, Monday) | `week:2026-05-04` |
| month | `month:YYYY-MM-DD` (month start) | `month:2026-05-01` |
| backlog | `backlog` | `backlog` |

These IDs never correspond to persisted documents. The reactive storage layer already indexes items by `(relationKey, parentID)` — this mechanism works for virtual parents just the same.

**Relation properties:**
- `ordered: true` (tasks have a `seq` within each period)
- `multiparent: false` (a task is scheduled to at most one period at a time)
- `required: false` (unscheduled tasks have no entry for this relation)

This approach requires **no new storage primitives** — it reuses the existing `SingleRelationPlacement` indexing already present in `ReactiveStorage`.

### What Does Not Change

The existing `builtin.elemOf` (main parent-child) and `builtin.labels` relations are unaffected. A task simultaneously has a list parent (via `elemOf`) and a scheduled date (via `plannedFor`). These are independent.

---

## Implementation Steps

### Step 1 — Domain: `plannedFor` Relation Definition

**File:** `src/domain/types.ts` (additions only)

Add to `BuiltinRels`:
```ts
plannedFor: "builtin.plannedFor",
```

Add a helper type:
```ts
export type ScheduleGranularity = 'day' | 'week' | 'month';

export type ScheduleTarget =
  | { granularity: ScheduleGranularity; date: string }  // ISO date of period start
  | { granularity: 'backlog' };
```

**File:** `src/domain/relations.ts`

Register `builtin.plannedFor` in `BuiltInRelationsConfig` alongside the existing relations:
```ts
{
  _id: BuiltinRels.plannedFor,
  text: "Planned for",
  ordered: true,
  multiparent: false,
  required: false,
}
```

**File:** `src/domain/item.ts`

Add a computed getter to `Item`:
```ts
get scheduledFor(): ScheduleTarget | null
```
This parses `this.relations['builtin.plannedFor']` and decodes the synthetic parent ID back into a `ScheduleTarget`.

Also add support for a `repeat` field on the raw doc type (optional):
```ts
repeat?: { increment: number; unit: ScheduleGranularity }
```

---

### Step 2 — Date Utilities

**New file:** `src/utils/date-utils.ts`

Port and TypeScript-ify the logic from `old-app/frontend/js/time-utils.js`. Functions needed:

- `todayIso()`, `weekStartIso(date?)`, `monthStartIso(date?)` — return ISO strings for current periods
- `parentIdForTarget(target: ScheduleTarget): string` — encodes a `ScheduleTarget` into a synthetic parent ID
- `targetFromParentId(id: string): ScheduleTarget | null` — reverse decode
- `formatDateChip(target: ScheduleTarget): string` — "Today", "Tomorrow", "This week", "2026.05.07–11", "2026.05", etc.
- `formatPeriodHeader(target: ScheduleTarget): string` — longer label used as section heading in the calendar
- `formatPeriodSubheader(target: ScheduleTarget): string | null` — secondary line (absolute date range for "This week", etc.)
- `periodType(target: ScheduleTarget): 'past' | 'current' | 'future'` — drives section styling
- `calcRepeatDate(current: ScheduleTarget, repeat: { increment: number; unit: ScheduleGranularity }): ScheduleTarget`
- `iteratePeriods(granularity: ScheduleGranularity, from: string, to: string): string[]` — returns ISO start dates for all periods in range

Use the native `Intl.DateTimeFormat` API (no external date library dependency required, though `date-fns` is acceptable if already in `package.json`).

---

### Step 3 — Scheduling Operations in `item-controller.ts`

Add methods to `ItemController` (or a new `ScheduleController` if keeping concerns separate):

```ts
scheduleTo(item: Item, target: ScheduleTarget): Promise<void>
unschedule(item: Item): Promise<void>
bulkScheduleTo(items: Item[], target: ScheduleTarget): Promise<void>
setRepeat(item: Item, repeat: { increment: number; unit: ScheduleGranularity } | null): Promise<void>
```

`scheduleTo` calculates a `seq` by inserting at the end of the target period's existing children (same pattern as the existing `appendTo` logic). It writes a single `ItemRelations` update that replaces the previous `plannedFor` entry.

`unschedule` writes `{ 'builtin.plannedFor': undefined }` to clear the relation.

On task completion (`markDone` or equivalent), if the item has a `repeat` field, call `scheduleTo` with the next calculated period automatically.

---

### Step 4 — CalendarView Component

**New file:** `src/views/CalendarView.vue`

Top-level view, registered at route `/calendar`.

State it owns:
```ts
futureSectionsToShow: Record<'days'|'weeks'|'months', number>
pastSectionsToShow:   Record<'days'|'weeks'|'months', number>
// loaded from/saved to localStorage, defaults: days=2, weeks=1, months=1
```

Computed:
- `todayIso`, `thisWeekIso`, `thisMonthIso` — recalculated at midnight (use `setTimeout` until next midnight on `onMounted`)
- `columns` — array of column descriptors: Days, Weeks, Months, Backlog (order configurable via a setting stored in localStorage, matching old-app's layout mechanism)
- For each time-unit column, `allSections(granularity)` returns an array of section objects with:
  - `parentId: string`
  - `target: ScheduleTarget`
  - `tasks: Item[]` — from `storage.getChildren(parentId, 'builtin.plannedFor')`
  - `type: 'past'|'current'|'future'`
  - `previousEmptySections: number`
- Auto-expand past: same logic as old-app — if the earliest period with overdue tasks is further in the past than current `pastSectionsToShow`, bump it up

Layout: horizontal scroll of columns, matching `ListOfLists.vue` style. Each column contains a stacked list of `CalendarSection` components.

---

### Step 5 — CalendarSection Component

**New file:** `src/components/CalendarSection.vue`

Props: `section` (descriptor from Step 4), `granularity`.

Renders:
- A section header with the period label (primary + optional secondary text from `formatPeriodHeader`)
- A count badge when `previousEmptySections > 0` ("+ N empty")
- A visual treatment for `past` vs `current` vs `future` (opacity / border-color)
- The task list using the existing `ElementList` + `ItemCard` components
- An `AddItem` button pre-wired to create tasks in this time period (sets `plannedFor` on creation)

---

### Step 6 — Column Navigation Component

**New file:** `src/components/CalendarColumnNav.vue`

Controls at the bottom (and/or top) of each time-unit column:

- "Show previous" / "Reset" (past side)
- "Show more" / "Reset" (future side)

Emits events handled by `CalendarView`. Uses the same `increaseProgressively` doubling logic from the old app.

---

### Step 7 — DateMenu Component

**New file:** `src/components/DateMenu.vue`

A `BaseMenu`-based dropdown. Props: `item: Item` (single-task mode) or `items: Item[]` (bulk mode).

Menu items:
- Today
- Tomorrow
- This week
- Next week
- This month
- Backlog / Unplanned
- Remove date (disabled if not scheduled)
- Other date… (opens `DatePickerDialog`)

Each option is disabled if the item is already scheduled there.

Bulk mode: same options, applies `bulkScheduleTo` from Step 3.

---

### Step 8 — DatePickerDialog Component

**New file:** `src/components/DatePickerDialog.vue`

A modal dialog (reuse `BaseMenu` overlay pattern or add a simple `<dialog>` element). Contains:

- Quick-pick buttons: "In 2 weeks", "In 3 weeks", "Next month", "In 2 months"
- An `<input type="date">` for arbitrary day selection
- Week and month selection: two extra `<input type="week">` / `<input type="month">` fields

On confirm, calls `scheduleTo` with the appropriate `ScheduleTarget`.

Triggered via a global event bus or a reactive singleton (matching existing `BaseMenu` patterns in the new app).

---

### Step 9 — DateChip in ItemCard / ItemHeader

**Files:** `src/components/ItemCard.vue`, `src/components/ItemHeader.vue`

When `item.scheduledFor !== null`, render a small chip/badge using `formatDateChip(item.scheduledFor)`. Clicking the chip opens `DateMenu` for that item.

Style: subtle, secondary text color, calendar icon prefix. Matches the visual weight of label badges already shown in `ItemHeader`.

---

### Step 10 — Repeat UI (stretch)

**File:** `src/components/ActionMenu.vue` (additions)

Add a "Set repeat…" sub-menu or inline control that lets the user set `increment` and `unit` on a task. When the task is marked done (existing `markDone` flow in `ItemController`), the controller checks for `repeat` and calls `scheduleTo` with the next period automatically.

This can be deferred if calendar core (Steps 1–9) is sufficient for initial use.

---

### Step 11 — Router and Navigation

**File:** `src/router/index.ts`

Add route:
```ts
{ path: '/calendar', component: () => import('../views/CalendarView.vue') }
```

**File:** `src/components/Topbar.vue`

Add a "Calendar" tab / button alongside existing navigation.

---

## File Checklist

| File | Status | Notes |
|------|--------|-------|
| `src/domain/types.ts` | modify | add `BuiltinRels.plannedFor`, `ScheduleGranularity`, `ScheduleTarget` |
| `src/domain/relations.ts` | modify | register `builtin.plannedFor` in config |
| `src/domain/item.ts` | modify | add `scheduledFor` getter, `repeat` field |
| `src/utils/date-utils.ts` | new | all date math and formatting |
| `src/item-controller.ts` | modify | `scheduleTo`, `unschedule`, `bulkScheduleTo`, `setRepeat`, repeat-on-done |
| `src/views/CalendarView.vue` | new | main calendar view |
| `src/components/CalendarSection.vue` | new | single time-period section |
| `src/components/CalendarColumnNav.vue` | new | show more / show previous controls |
| `src/components/DateMenu.vue` | new | quick-schedule dropdown |
| `src/components/DatePickerDialog.vue` | new | custom date picker |
| `src/components/ItemCard.vue` | modify | add date chip |
| `src/components/ItemHeader.vue` | modify | add date chip |
| `src/components/ActionMenu.vue` | modify | add "Schedule…" and optional "Set repeat…" entries |
| `src/router/index.ts` | modify | add `/calendar` route |
| `src/components/Topbar.vue` | modify | add calendar navigation link |

---

## Open Questions

1. **Date library**: The old app uses `moment.js`. The new app has no date library yet. `date-fns` (tree-shakable, immutable) is a better fit for a modern codebase. Needs a decision before Step 2.

2. **Add-item in calendar sections**: When creating a task from a calendar section, should it be added to a default list as well (the `builtin.elemOf` relation also needs a parent)? A sensible default is a user-configurable "default list", or the first list. This needs a UX decision.

3. **Backlog representation**: In the old app, backlog is a special `list`-class parent key. In the new app, an unscheduled task simply has no `plannedFor` entry. The "Backlog" column in the calendar would show all tasks without a `plannedFor` relation. This requires a dedicated query, not just `getChildren`. The `ReactiveStorage` layer may need a `getUnscheduled()` helper.

4. **Column layout persistence**: Old app stores layout order in a CouchDB document. New app could use localStorage for simplicity (at least initially).

5. **Repeat on-done trigger**: The `markDone` path needs to be identified in the new app before Step 10. If `doneAt` is set by a relation update elsewhere, the trigger point may differ from the old app.
