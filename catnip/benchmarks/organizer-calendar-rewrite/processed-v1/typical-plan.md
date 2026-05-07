# Plan: Calendar & Time-Based Planning Features

## Context

**Old app**: Vue 2 + JavaScript. Calendar features are fully implemented.  
**New app**: Vue 3 + TypeScript + Vite. Architecture is in place; calendar features are entirely missing.

The goal is to reimplement the calendar and time-based planning features in the new app using its architecture properly, not to port code mechanically. Data format compatibility with the old app is not required.

---

## Feature Scope

### In scope

| Feature | Notes |
|---|---|
| 3-level time hierarchy (day / week / month) | Core calendar model |
| Backlog (unplanned items) | Items with no time assignment |
| TimeBoard multi-column view | Main calendar UI |
| Smart date formatting ("Today", "Tomorrow", …) | UX polish |
| Quick-schedule context menu | Today, Tomorrow, This week, Next week, This month, Remove |
| Date-picker dialog for arbitrary dates | Custom scheduling |
| Date chip on task cards | Shows where the item is planned |
| Display settings | Toggle column types, show more / show previous |
| Recurring tasks | `repeat` field; advance date on completion |

### Out of scope (deferred)

| Feature | Reason |
|---|---|
| Google Calendar sync | Large independent feature with its own OAuth flow |

---

## Architecture Decision

The new app's core abstraction is items connected by relations. Time scheduling fits this model directly: introduce a `builtin.plannedFor` relation whose parent IDs are **synthetic date strings** computed from the date rather than stored documents.

Synthetic parent ID format:

| Granularity | Parent ID | Example |
|---|---|---|
| Day | `day:YYYY-MM-DD` | `day:2026-05-07` |
| Week | `week:YYYY-WNN` (ISO week) | `week:2026-W19` |
| Month | `month:YYYY-MM` | `month:2026-05` |

These IDs never correspond to persisted documents. The reactive storage layer indexes items by `(relationKey, parentId)` — this mechanism works for virtual parents just the same, so no new storage primitives are needed.

---

## Data Model

### `builtin.plannedFor` relation

Register in `BuiltinRels` and `RelationRegistry`:

```typescript
{
  key: "builtin.plannedFor",
  ordered: true,        // items have a seq within each bucket
  singleParent: true,   // a task is planned for at most one period at a time
  required: false,      // unscheduled tasks simply have no entry
}
```

Tasks gain this relation when scheduled; removing it moves the task to the backlog:

```typescript
// inside item.relations:
"builtin.plannedFor": {
  parentId: "week:2026-W19",
  seq: "c",
}
```

### `repeat` field on items

```typescript
repeat?: {
  unit: 'day' | 'week' | 'month';
  increment: number;
}
```

---

## Implementation Plan

### Phase 1 — Domain layer

**`src/domain/types.ts`** — add `plannedFor` to `BuiltinRels`; add `Granularity` type (`'day' | 'week' | 'month'`).

**`src/domain/relations.ts`** — register `builtin.plannedFor` in the relation config with the characteristics above.

**`src/domain/item.ts`** — add optional `repeat` field; add a `scheduledFor` computed getter that parses `relations['builtin.plannedFor']` and returns a typed value (granularity + date) or `null`.

---

### Phase 2 — Date utilities

**New file: `src/domain/time-utils.ts`**

Port and TypeScript-ify the logic from `old-app`'s `time-utils.js`. Use the native `Intl.DateTimeFormat` API — do not add moment.js or another date library.

Key exports:

```typescript
// Bucket ID generation and parsing
function bucketId(granularity: Granularity, date: Date): string
function parseBucketId(id: string): { granularity: Granularity; date: Date }

// Human-readable labels
function formatBucketLabel(granularity: Granularity, date: Date): string
// e.g. "Today", "Tomorrow", "This week", "W19 May 5–11", "May 2026"

// Relative classification for styling
type TimeStatus = 'past' | 'current' | 'future'
function timeStatus(granularity: Granularity, date: Date): TimeStatus

// Navigation
function prevBucket(granularity: Granularity, date: Date): Date
function nextBucket(granularity: Granularity, date: Date): Date

// Recurrence
function advanceByRepeat(date: Date, repeat: { unit: Granularity; increment: number }): Date
```

---

### Phase 3 — Scheduling operations

**`src/item-controller.ts`** — add methods:

```typescript
scheduleTo(item: Item, granularity: Granularity, date: Date): Promise<void>
unschedule(item: Item): Promise<void>
bulkScheduleTo(items: Item[], granularity: Granularity, date: Date): Promise<void>
```

`scheduleTo` inserts at the end of the target bucket (same `seq`-calculation pattern as the existing `appendTo` logic) and writes a single `ItemRelations` update replacing any previous `plannedFor` entry.

On task completion, if the item has a `repeat` field, call `scheduleTo` automatically with the next calculated period.

---

### Phase 4 — Calendar view and components

**New file: `src/views/CalendarView.vue`**

Top-level view, registered at route `/calendar`. Manages:
- Which column types are visible (days / weeks / months / backlog)
- How many past and future sections to show per column type ("show more" / "show previous" with progressive doubling)
- Layout and visibility preferences persisted across sessions

Renders a horizontal multi-column layout. Because `ReactiveStorage` indexes are Vue-reactive, column contents update automatically when tasks are scheduled or rescheduled.

**New file: `src/components/TimeBucketColumn.vue`**

Props: `bucketId`, `granularity`, `timeStatus`.

Renders a column header with the formatted label and past/current/future styling, then the list of items using the existing `ItemCard` and `ElementList` components. Accepts drag-and-drop to move items between buckets, delegating `seq` calculation to the existing relation driver.

**New file: `src/components/CalendarSettings.vue`**

Panel for toggling each column type (days / weeks / months / backlog) on or off.

---

### Phase 5 — Scheduling UI

**New file: `src/components/DateMenu.vue`**

A dropdown (extending `BaseMenu`) with quick-schedule options:

| Option | Action |
|---|---|
| Today | `scheduleTo(item, 'day', today)` |
| Tomorrow | `scheduleTo(item, 'day', tomorrow)` |
| This week | `scheduleTo(item, 'week', thisWeekStart)` |
| Next week | `scheduleTo(item, 'week', nextWeekStart)` |
| This month | `scheduleTo(item, 'month', thisMonthStart)` |
| Remove date | `unschedule(item)` |
| Other date… | opens `DatePickerDialog` |

Bulk mode: same options, applies `bulkScheduleTo`.

**New file: `src/components/DatePickerDialog.vue`**

A modal with:
- Relative shortcuts: "In 2 weeks", "In 3 weeks", "Next month", "In 2 months"
- A native `<input type="date">` for arbitrary day selection, with buttons to switch to week or month granularity

**`src/components/ItemCard.vue`** — when `item.scheduledFor !== null`, render a small date chip using `formatBucketLabel`. Clicking the chip opens `DateMenu` for that item.

**`src/components/ActionMenu.vue`** — add a "Schedule…" option that opens `DateMenu`.

---

### Phase 6 — Navigation and routing

**`src/router/index.ts`** — add route:
```typescript
{ path: '/calendar', component: () => import('../views/CalendarView.vue') }
```

**`src/components/Topbar.vue`** — add a "Calendar" link alongside existing navigation.

---

## File Summary

| File | Action | Notes |
|---|---|---|
| `src/domain/types.ts` | Modify | Add `plannedFor` to `BuiltinRels`; add `Granularity` type |
| `src/domain/relations.ts` | Modify | Register `builtin.plannedFor` |
| `src/domain/item.ts` | Modify | `scheduledFor` getter, `repeat` field |
| `src/domain/time-utils.ts` | Create | Date formatting, bucket ID helpers, recurrence math |
| `src/item-controller.ts` | Modify | `scheduleTo`, `unschedule`, `bulkScheduleTo`, repeat-on-done |
| `src/views/CalendarView.vue` | Create | Top-level calendar view |
| `src/components/TimeBucketColumn.vue` | Create | Single time-bucket column |
| `src/components/CalendarSettings.vue` | Create | Column visibility toggles |
| `src/components/DateMenu.vue` | Create | Quick-schedule dropdown |
| `src/components/DatePickerDialog.vue` | Create | Arbitrary date modal |
| `src/components/ItemCard.vue` | Modify | Add date chip |
| `src/components/ActionMenu.vue` | Modify | Add "Schedule…" entry |
| `src/router/index.ts` | Modify | Add `/calendar` route |
| `src/components/Topbar.vue` | Modify | Add calendar navigation link |

---

## Implementation Order

1. `src/domain/time-utils.ts` — pure functions, easy to unit-test in isolation
2. `src/domain/types.ts` + `src/domain/relations.ts` + `src/domain/item.ts` — domain type and relation registration
3. `src/item-controller.ts` — scheduling operations and repeat-on-done logic
4. `src/components/TimeBucketColumn.vue` — single column (read-only first, verify storage queries work end-to-end)
5. `src/views/CalendarView.vue` — top-level shell with show-more navigation
6. `src/components/DateMenu.vue` + `src/components/DatePickerDialog.vue` — scheduling actions
7. Wire `DateMenu` into `ActionMenu.vue`; add date chip to `ItemCard.vue`
8. Drag-and-drop rescheduling across columns
9. `src/components/CalendarSettings.vue` — visibility toggles
10. `src/router/index.ts` + `src/components/Topbar.vue` — navigation

---

## Key Design Decisions

**`plannedFor` is a standard relation.** It uses the same `Relation` class, `RelationDriver`, and `ItemController` machinery as the existing `mainRelation`. No special-casing in the storage or query layers is needed.

**Virtual time-bucket IDs.** Days, weeks, and months are not stored as database documents; their IDs are deterministic computed strings. The storage layer's `(relationKey, parentId)` index works identically for virtual parents.

**No moment.js.** Use the native `Intl.DateTimeFormat` API and standard `Date`. The formatting requirements (relative names, ISO week numbers) are modest enough that a library dependency is unnecessary.

**Reuse existing components.** `ItemCard`, `ElementList`, `ActionMenu`, and `BaseMenu` are already built. The calendar view composes them rather than reimplementing item rendering.
