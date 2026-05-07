# Plan: Calendar & Time-Based Planning Features (New App)

## Context

The old app (`old-app/`) is a Vue 2 + JavaScript TODO application with a sophisticated
calendar system. The new app (`new-app/`) is a Vue 3 + TypeScript rewrite with a clean
3-layer architecture (domain / implementation / UI) and a flexible relation/type registry,
but no time-based planning yet.

This plan describes how to bring the calendar and time-based planning features into the
new app in a way that fits its architecture rather than porting the old code verbatim.

---

## Feature Scope

### In scope

| Feature | Old-app source | Notes |
|---|---|---|
| 3-level time hierarchy (day / week / month) | `time-board.vue`, `time-utils.js` | Core calendar model |
| Backlog (unplanned items) | `reactive-cache.js` | Items with no time assignment |
| TimeBoard multi-column view | `time-board.vue` | Main calendar UI |
| Smart date formatting ("Today", "Tomorrow", …) | `time-utils.js` | UX polish |
| Quick-schedule context menu | `date-menu-content.vue` | Today, Tomorrow, This Week, … |
| Date-picker dialog for arbitrary dates | `date-dialog.vue` | Custom scheduling |
| TimeBoard display settings | `time-board-settings.vue` | Toggle columns, show more |
| Drag-to-reschedule / reorder within a column | `ordered-relation.js` + `time-board.vue` | Mudder ordering already in new app |

### Out of scope (deferred)

- **Google Calendar sync** — the `gcalendar-utils.js` integration is a large, independent
  feature with its own OAuth flow. Defer to a separate effort.
- **Recurring tasks** — the `calcRepeatDate()` / `repeat` field logic depends on
  well-defined task completion flows that are not yet implemented in the new app.
- **Duration / time-slot display** — the `dur` field (15-min increments) from the old app
  is rarely used and can be added later.

---

## Architecture Decision: How to Model Time Units

The new app's core abstraction is *items connected by relations*. There are two ways to
represent a scheduled task's time assignment:

**Option A — Plain property on each item**
Add `scheduledDate` + `scheduledGranularity` (day / week / month) fields directly to
item documents. Calendar views filter and group by these fields; ordering within a bucket
is a separate `planSeq` field, managed outside the relation system.

**Option B — Time-bucket items connected by a relation** (recommended)
Create lightweight "time-bucket" items (one per calendar day/week/month as needed) and
use the existing `plannedFor` relation to link tasks to them. The relation system's
existing ordering infrastructure (Mudder sequences via `relation-driver.ts`) handles
intra-bucket ordering automatically.

Option B is recommended because:
- Ordering within a bucket is handled by existing, tested infrastructure (no new seq logic).
- The relation registry pattern already used in the new app handles this cleanly.
- `ReactiveStorage` already maintains an `indexes` map keyed by parent ID, so calendar
  grouping is a zero-cost query.
- Bucket items can carry metadata (colour, notes) in the future without schema changes.

The trade-off is that time-bucket items appear in the database alongside task items.
This is managed by giving them a dedicated `type: "timeBucket"` so they are invisible
outside the calendar view and excluded from list/topic views automatically.

---

## Data Model

### New built-in item type: `timeBucket`

```typescript
// added to BuiltinTypes in domain/types.ts
"timeBucket": {
  key: "builtin.timeBucket",
  allowedChildTypes: ["task", "note"],  // same as list
  isLeaf: false,
}
```

Each `timeBucket` document:
```typescript
{
  _id: "timeBucket:day:2026-05-07",   // deterministic IDs
  type: "builtin.timeBucket",
  text: "2026-05-07",                  // ISO date string or "2026-W19" or "2026-05"
  granularity: "day" | "week" | "month",
  // standard BaseDoc fields
}
```

ID format by granularity:
- Day: `timeBucket:day:YYYY-MM-DD`
- Week: `timeBucket:week:YYYY-WNN` (ISO week number)
- Month: `timeBucket:month:YYYY-MM`

Deterministic IDs mean no duplicate buckets and trivial upserts.

### New built-in relation: `plannedFor`

```typescript
// added to BuiltinRels in domain/types.ts
"plannedFor": {
  key: "builtin.plannedFor",
  singleParent: true,       // a task is planned for exactly one time unit at a time
  ordered: true,            // tasks within a bucket have a user-defined order
  allowedParentTypes: ["timeBucket"],
}
```

Tasks gain this relation when scheduled:
```typescript
// inside item's relations map:
"builtin.plannedFor": {
  parentId: "timeBucket:day:2026-05-07",
  seq: "c",
}
```

Removing the relation (setting it to `undefined`) moves the task to the backlog.

---

## Implementation Plan

### Phase 1 — Domain & type registration

**Files to change:**
- `src/domain/types.ts` — add `timeBucket` to `BuiltinTypes`, add `plannedFor` to
  `BuiltinRels`.
- `src/domain/item.ts` — exclude `timeBucket` items from `LeafLikeTypes`; add helper
  `item.granularity` getter for time-bucket items.
- `src/domain/relations.ts` — add constraint: a `plannedFor` relation's parent must be a
  `timeBucket`.

No changes to `relation-driver.ts` or `reactive-storage.ts`; they are granularity-agnostic.

---

### Phase 2 — Time utilities (TypeScript port of `time-utils.js`)

Create `src/domain/time-utils.ts`.

Key exports:
```typescript
// Parse / generate bucket IDs
function bucketId(granularity: Granularity, date: Date): string
function parseBucketId(id: string): { granularity: Granularity; date: Date }

// Human-readable labels
function formatDay(date: Date): string   // "Today", "Tomorrow", "Mon 5 May", …
function formatWeek(date: Date): string  // "This week", "Next week", "W19 May 5–11"
function formatMonth(date: Date): string // "This month", "May 2026", …

// Relative classification for styling
type TimeStatus = "past" | "current" | "future"
function timeStatus(granularity: Granularity, date: Date): TimeStatus

// Navigation helpers
function prevBucket(granularity: Granularity, date: Date): Date
function nextBucket(granularity: Granularity, date: Date): Date
function bucketContains(granularity: Granularity, bucketDate: Date, target: Date): boolean
```

Use the native `Intl.DateTimeFormat` API instead of moment.js (moment is not a dependency
of the new app and should not be added). ISO week calculation is ~15 lines of arithmetic.

---

### Phase 3 — TimeBucketService (implementation layer)

Create `src/implementation/time-bucket-service.ts`.

Responsibilities:
- `ensureBucket(granularity, date)`: upsert-or-return a `timeBucket` item for the given
  period. Uses the deterministic ID so concurrent calls are idempotent.
- `scheduleTo(itemId, granularity, date, position?)`: calls `ensureBucket`, then calls
  `ItemController.replaceParents()` on the `plannedFor` relation.
- `unschedule(itemId)`: calls `ItemController.removeParents()` on `plannedFor`.
- `getPlannedItems(granularity, date)`: reads from `ReactiveStorage.indexes` — no extra
  query needed.
- `getBacklogItems()`: items of type task/note with no `plannedFor` relation.

Expose via Vue plugin so components access it as `inject('timeBucketService')`.

---

### Phase 4 — TimeBoard view

Create `src/views/TimeBoardView.vue`.

**Layout:** Three resizable column groups (days | weeks | months) plus an optional backlog
column. Each column group shows N consecutive time buckets. The user can reveal more
with "Show earlier" / "Show more" buttons at the top and bottom of each group.

**State (within the component, using Vue 3 `ref`/`computed`):**
```typescript
const shownDays: Ref<number>    // default 7 (today ± a few)
const shownWeeks: Ref<number>   // default 4
const shownMonths: Ref<number>  // default 3
const startDay: Ref<Date>       // first day currently in view (default: today - 2)
```

**Column generation:** A `computed` property builds an array of column descriptors:
```typescript
type ColumnDescriptor =
  | { kind: "bucket"; granularity: Granularity; date: Date; items: readonly Item[] }
  | { kind: "backlog"; items: readonly Item[] }
```

Because `ReactiveStorage.indexes` is Vue-reactive, `items` in each descriptor updates
automatically when tasks are scheduled or rescheduled.

**Sub-components to create:**
- `TimeBucketColumn.vue` — renders one time bucket: header with formatted date + status
  class, list of `ItemCard` components, drag-drop target.
- `TimeBoardSettings.vue` — checkboxes to show/hide each column type and backlog; show
  the column-width ratio slider.

**Drag-and-drop rescheduling:** Use the native HTML5 drag-and-drop API (no library
needed). Dragging an `ItemCard` into a `TimeBucketColumn` calls
`timeBucketService.scheduleTo(...)`. The `position` argument is calculated from the
drop target's index in the column's item list, delegating sequence calculation to
`relation-driver.ts` as normal.

---

### Phase 5 — Scheduling UI

**`ScheduleMenu.vue`** (replaces `date-menu-content.vue`)

A popover component with quick-schedule buttons:

| Button | Action |
|---|---|
| Today | `scheduleTo(id, "day", today)` |
| Tomorrow | `scheduleTo(id, "day", tomorrow)` |
| This week | `scheduleTo(id, "week", thisWeekMonday)` |
| Next week | `scheduleTo(id, "week", nextWeekMonday)` |
| This month | `scheduleTo(id, "month", firstOfMonth)` |
| Pick date… | open `DatePickerDialog` |
| Remove date | `unschedule(id)` |

Integrate into the existing `ActionMenu.vue` by adding a "Schedule" option that renders
`ScheduleMenu` as a sub-menu or popover.

**`DatePickerDialog.vue`** (replaces `date-dialog.vue`)

A modal with:
- A native `<input type="date">` for selecting a specific day, plus buttons to switch to
  week or month granularity for the selected date.
- Relative shortcuts: "+1 week", "+2 weeks", "+1 month", "+2 months".
- Confirm / Cancel buttons.

Use `<dialog>` element with `showModal()` instead of a Vue-Material modal.

---

### Phase 6 — Navigation & routing

Add a `/time` route in `src/router/index.ts` pointing to `TimeBoardView`. Add a link in
`Topbar.vue` next to the existing root navigation.

No changes to the existing routing logic are needed; `TimeBoardView` is a self-contained
top-level view.

---

## File Summary

| File | Action | Notes |
|---|---|---|
| `src/domain/types.ts` | Modify | Add `timeBucket` type, `plannedFor` relation |
| `src/domain/item.ts` | Modify | `granularity` getter, exclude `timeBucket` from leaf types |
| `src/domain/relations.ts` | Modify | Parent-type constraint for `plannedFor` |
| `src/domain/time-utils.ts` | Create | Date formatting, bucket ID helpers |
| `src/implementation/time-bucket-service.ts` | Create | Scheduling operations |
| `src/views/TimeBoardView.vue` | Create | Main calendar view |
| `src/components/TimeBucketColumn.vue` | Create | Single bucket column |
| `src/components/TimeBoardSettings.vue` | Create | Column visibility settings |
| `src/components/ScheduleMenu.vue` | Create | Quick-schedule popover |
| `src/components/DatePickerDialog.vue` | Create | Arbitrary date modal |
| `src/components/ActionMenu.vue` | Modify | Add "Schedule" option |
| `src/router/index.ts` | Modify | Add `/time` route |
| `src/views/Topbar.vue` (or equivalent) | Modify | Add TimeBoard navigation link |

---

## Suggested Implementation Order

1. `time-utils.ts` — pure functions, easy to unit-test in isolation.
2. `types.ts` + `item.ts` + `relations.ts` — domain type registration.
3. `time-bucket-service.ts` — scheduling logic, depends on 1 & 2.
4. `TimeBucketColumn.vue` + `TimeBoardView.vue` — basic read-only calendar view (no
   drag-drop yet), verify that creating and querying buckets works end-to-end.
5. `ScheduleMenu.vue` + `DatePickerDialog.vue` — add scheduling actions.
6. Integrate `ScheduleMenu` into `ActionMenu.vue`.
7. Drag-and-drop reordering within and across columns.
8. `TimeBoardSettings.vue` — column visibility toggles.
9. `Topbar.vue` + router — wire up navigation.

---

## Key Differences from Old App (by design)

- **No moment.js** — native `Intl` + lightweight ISO week arithmetic.
- **No implicit cache invalidation** — Vue 3 reactivity from `ReactiveStorage.indexes`
  makes manual cache management unnecessary.
- **Deterministic bucket IDs** — no "find or create" race conditions; upserts are safe.
- **Type-safe scheduling** — `Granularity` is a TypeScript union, not a magic string.
- **`plannedFor` is a first-class relation** — benefits from the existing cycle detection,
  type validation, and ordering infrastructure without special-casing.
