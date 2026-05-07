# Plan: Calendar & Time-Based Planning Features

## Context

**Old app**: Vue 2 + JavaScript + Moment.js. Calendar features are fully implemented.  
**New app**: Vue 3 + TypeScript + Vite. Architecture is in place; calendar features are entirely missing.

The goal is to reimplement the calendar and time-based planning features in the new app using its architecture properly, not to port code mechanically. Data format compatibility with the old app is not required.

---

## New App Architecture (Relevant Patterns)

Relations are the core abstraction. Each relation has three layers:
1. **RelationController** (`src/domain/relations.ts`) — validates constraints, calculates placements
2. **RelationDriver** (`src/implementation/relation-driver.ts`) — mudder-based sequence math
3. **ItemController** (`src/item-controller.ts`) — top-level orchestrator; groups, persists, delegates

Built-in types and relations live in `src/domain/types.ts` (`BuiltinTypes`, `BuiltinRels`). Item relations are stored as `Record<RelationKey, Record<parentId, { seq?: string }>>` on each document. `ReactiveStorage` maintains an `indexes` map keyed by `(relationKey, parentId)` that is Vue-reactive — calendar views can read from it without any extra query logic.

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
| Date-picker dialog for arbitrary dates | Custom scheduling, bulk mode |
| Date chip on task cards | Shows scheduled period, opens date menu on click |
| Display settings | Toggle column types, show more / show previous |
| Drag-to-reschedule / reorder within a column | Mudder ordering already in new app |
| Recurring tasks | `repeat` field; advance date on completion |

### Out of scope (deferred)

| Feature | Reason |
|---|---|
| Google Calendar sync | Large independent feature with its own OAuth flow — see optional Phase 7 |

---

## Architecture Decision

The new app models everything as items connected by relations. There are two broad approaches for representing a scheduled task's time assignment:

**Option A — Plain property on each item**: add `scheduledDate` + `scheduledGranularity` fields directly to item documents. Ordering within a bucket requires a separate `planSeq` field managed outside the relation system.

**Option B — `plannedFor` relation with virtual parent IDs** *(recommended)*: add a `builtin.plannedFor` relation whose parent IDs are deterministic computed strings (`day:2026-05-07`, `week:2026-W19`, `month:2026-05`). These IDs never correspond to stored documents; `ReactiveStorage` indexes items by `(relationKey, parentId)` regardless. Intra-bucket ordering is handled by the existing mudder-based `RelationDriver` with no new infrastructure.

Option B is preferred because ordering reuses existing, tested code; calendar grouping is a zero-cost index lookup; and `plannedFor` benefits from the existing cycle detection, type validation, and single-parent enforcement without special-casing anywhere.

The `builtin.elemOf` (list parent) and `builtin.labels` relations are unaffected. A task simultaneously holds a list parent and a scheduled date — these are independent.

---

## Data Model

### `builtin.plannedFor` relation

```typescript
// added to BuiltinRels in src/domain/types.ts
export type Granularity = 'day' | 'week' | 'month';

export type ScheduleTarget =
  | { granularity: Granularity; date: string }  // ISO period-start date
  | { granularity: 'backlog' };
```

Register in `BuiltinRelationsConfig` in `src/domain/relations.ts`:

```typescript
{
  key: "builtin.plannedFor",
  ordered: true,       // tasks have a seq within each bucket
  singleParent: true,  // at most one time period at a time
  required: false,     // unscheduled tasks have no entry
}
```

Synthetic parent ID format:

| Granularity | Parent ID | Example |
|---|---|---|
| Day | `day:YYYY-MM-DD` | `day:2026-05-07` |
| Week | `week:YYYY-WNN` (ISO week) | `week:2026-W19` |
| Month | `month:YYYY-MM` | `month:2026-05` |

### `repeat` field on items

```typescript
// optional addition to BaseDoc in src/domain/item.ts
repeat?: { increment: number; unit: Granularity }
```

---

## Implementation Plan

### Phase 1 — Domain layer

**`src/domain/types.ts`** — add `plannedFor` to `BuiltinRels`; add `Granularity` and `ScheduleTarget` types.

**`src/domain/relations.ts`** — register `builtin.plannedFor` in `BuiltinRelationsConfig`.

**`src/domain/item.ts`** — add optional `repeat` field; add a `scheduledFor` computed getter that parses `relations['builtin.plannedFor']` and returns a `ScheduleTarget | null`.

No changes to `relation-driver.ts` or `reactive-storage.ts`; they are granularity-agnostic.

---

### Phase 2 — Date utilities

**New file: `src/domain/time-utils.ts`**

Port `old-app/frontend/js/time-utils.js` to TypeScript. Use the native `Intl.DateTimeFormat` API — do not add moment.js (ISO week calculation is ~15 lines of arithmetic).

Key exports:

```typescript
// Bucket ID generation and parsing
function bucketId(granularity: Granularity, date: Date): string
function parseBucketId(id: string): { granularity: Granularity; date: Date }

// Human-readable labels
function formatBucketLabel(granularity: Granularity, date: Date): string
// → "Today", "Tomorrow", "This week", "W19 May 5–11", "May 2026", …
function formatBucketSubheader(granularity: Granularity, date: Date): string | null
// → secondary line, e.g. absolute date range for "This week"

// Relative classification for styling
type TimeStatus = 'past' | 'current' | 'future'
function timeStatus(granularity: Granularity, date: Date): TimeStatus

// Navigation
function prevBucket(granularity: Granularity, date: Date): Date
function nextBucket(granularity: Granularity, date: Date): Date
function bucketContains(granularity: Granularity, bucketDate: Date, target: Date): boolean
function iteratePeriods(granularity: Granularity, from: Date, to: Date): Date[]

// Recurrence
function advanceByRepeat(date: Date, repeat: { unit: Granularity; increment: number }): Date
```

---

### Phase 3 — Scheduling operations

**`src/item-controller.ts`** — add methods:

```typescript
scheduleTo(item: Item, target: ScheduleTarget): Promise<void>
unschedule(item: Item): Promise<void>
bulkScheduleTo(items: Item[], target: ScheduleTarget): Promise<void>
setRepeat(item: Item, repeat: { increment: number; unit: Granularity } | null): Promise<void>
```

`scheduleTo` inserts at the end of the target bucket using the same `seq`-calculation pattern as the existing `appendTo` logic, and writes a single `ItemRelations` update replacing any previous `plannedFor` entry. `unschedule` writes `{ 'builtin.plannedFor': undefined }`.

On task completion, if the item has a `repeat` field, call `scheduleTo` automatically with the next calculated period.

---

### Phase 4 — Calendar view and components

**New file: `src/views/CalendarView.vue`**

Top-level view at route `/calendar`. Manages which column types are visible, how many past and future sections to show per type, and layout preferences persisted to a `meta.calendar-layout` document in PouchDB. Current-day values (`todayIso`, `thisWeekIso`, `thisMonthIso`) are recalculated at midnight via `setTimeout` on `onMounted`.

A `computed` property builds the reactive column list:

```typescript
type ColumnDescriptor =
  | { kind: 'bucket'; granularity: Granularity; date: Date; items: readonly Item[] }
  | { kind: 'backlog'; items: readonly Item[] }
```

Because `ReactiveStorage.indexes` is Vue-reactive, `items` updates automatically when tasks are scheduled or rescheduled — no manual cache invalidation needed.

**New file: `src/components/TimeBucketColumn.vue`**

Props: `bucketId`, `granularity`, `timeStatus`. Renders a header with the primary label from `formatBucketLabel` and optional secondary text from `formatBucketSubheader`, with past/current/future styling. Renders items using the existing `ElementList` + `ItemCard` components. Includes an "Add item" affordance that pre-sets `plannedFor` on creation.

Empty sections are hidden but a collapsed-count badge ("+ N empty") is shown on the adjacent visible section.

Drag-and-drop rescheduling uses the native HTML5 API (no library). Dropping an `ItemCard` onto a column calls `scheduleTo`; the drop position index is passed to `RelationDriver` for `seq` calculation as normal. `bucketContains` is used to short-circuit no-op drops.

**New file: `src/components/CalendarColumnNav.vue`**

Navigation controls rendered at the top and bottom of each column group: "Show previous" / "Reset" (past side) and "Show more" / "Reset" (future side). Uses a progressive-doubling strategy (same as old app's `increaseProgressively`). Emits events handled by `CalendarView`. Also auto-expands the past window when overdue tasks exist in a period earlier than the current `pastSectionsToShow` boundary.

**New file: `src/components/CalendarSettings.vue`**

Panel for toggling each column type (days / weeks / months / backlog) on or off, selecting custom lists to show as additional columns, and adjusting column-width ratios. Persists to the `meta.calendar-layout` document.

---

### Phase 5 — Scheduling UI

**New file: `src/components/DateMenu.vue`**

A dropdown (extending `BaseMenu`) with quick-schedule options. Supports both single-item and bulk mode (`items: Item[]`):

| Option | Action |
|---|---|
| Today | `scheduleTo(item, { granularity: 'day', date: today })` |
| Tomorrow | `scheduleTo(item, { granularity: 'day', date: tomorrow })` |
| This week | `scheduleTo(item, { granularity: 'week', date: thisWeekStart })` |
| Next week | `scheduleTo(item, { granularity: 'week', date: nextWeekStart })` |
| This month | `scheduleTo(item, { granularity: 'month', date: thisMonthStart })` |
| Remove date | `unschedule(item)` |
| Other date… | opens `DatePickerDialog` |

Each option is disabled if the item is already scheduled there. Bulk mode applies `bulkScheduleTo`.

**New file: `src/components/DatePickerDialog.vue`**

A `<dialog>` element using `showModal()`. Contains:
- Relative shortcuts: "In 2 weeks", "In 3 weeks", "Next month", "In 2 months"
- A native `<input type="date">` for arbitrary day selection, with buttons to switch to week or month granularity for the selected date
- Confirm / Cancel

**`src/components/ItemCard.vue`** and **`src/components/ItemHeader.vue`** — when `item.scheduledFor !== null`, render a small date chip using `formatBucketLabel`. Clicking the chip opens `DateMenu` for that item.

**`src/components/ActionMenu.vue`** — add a "Schedule…" option that opens `DateMenu`, and a "Set repeat…" sub-option that calls `setRepeat`.

---

### Phase 6 — Navigation and routing

**`src/router/index.ts`**:
```typescript
{ path: '/calendar', component: () => import('../views/CalendarView.vue') }
```

**`src/components/Topbar.vue`** — add a "Calendar" link alongside existing navigation.

---

### Phase 7 — Google Calendar integration (optional, defer until Phase 1–6 are solid)

**`src/implementation/gcalendar.ts`** — port `gcalendar-utils.js` to TypeScript: OAuth2 client-side flow, `loadEvents()` (upsert GCal events as items with `type: "builtin.event"` and `gcalId`), `exportToCalendar()`, `updateEvent()` with etag conflict detection.

Register `"builtin.event"` in `TypeRegistry`. Events have a start time and duration (`dur` in minutes) or a full-day flag; they are created/updated by sync and are read-only in most UIs.

Add a settings panel for authenticating with Google, selecting calendars to sync, and triggering manual sync.

---

## File Summary

| File | Action | Notes |
|---|---|---|
| `src/domain/types.ts` | Modify | Add `plannedFor` to `BuiltinRels`; `Granularity`, `ScheduleTarget` types |
| `src/domain/relations.ts` | Modify | Register `builtin.plannedFor` |
| `src/domain/item.ts` | Modify | `scheduledFor` getter, `repeat` field |
| `src/domain/time-utils.ts` | Create | Date formatting, bucket ID helpers, recurrence, navigation |
| `src/item-controller.ts` | Modify | `scheduleTo`, `unschedule`, `bulkScheduleTo`, `setRepeat`, repeat-on-done |
| `src/views/CalendarView.vue` | Create | Top-level calendar view |
| `src/components/TimeBucketColumn.vue` | Create | Single time-bucket column with drag-drop |
| `src/components/CalendarColumnNav.vue` | Create | Show more / show previous controls |
| `src/components/CalendarSettings.vue` | Create | Column visibility and layout settings |
| `src/components/DateMenu.vue` | Create | Quick-schedule dropdown (single + bulk) |
| `src/components/DatePickerDialog.vue` | Create | Arbitrary date modal |
| `src/components/ItemCard.vue` | Modify | Add date chip |
| `src/components/ItemHeader.vue` | Modify | Add date chip |
| `src/components/ActionMenu.vue` | Modify | Add "Schedule…" and "Set repeat…" entries |
| `src/router/index.ts` | Modify | Add `/calendar` route |
| `src/components/Topbar.vue` | Modify | Add calendar navigation link |

---

## Implementation Order

1. `src/domain/time-utils.ts` — pure functions, easy to unit-test in isolation
2. `src/domain/types.ts` + `src/domain/relations.ts` + `src/domain/item.ts` — domain registration
3. `src/item-controller.ts` — `scheduleTo`, `unschedule`, `bulkScheduleTo`, `setRepeat`, repeat-on-done
4. `src/components/TimeBucketColumn.vue` + `src/views/CalendarView.vue` — basic read-only view; verify storage queries and reactivity end-to-end
5. `src/components/CalendarColumnNav.vue` — show more / show previous navigation
6. `src/components/DateMenu.vue` + `src/components/DatePickerDialog.vue` — scheduling actions
7. Wire date chip into `ItemCard.vue` / `ItemHeader.vue`; wire `DateMenu` into `ActionMenu.vue`
8. Drag-and-drop rescheduling across columns
9. `src/components/CalendarSettings.vue` — visibility and layout toggles
10. `src/router/index.ts` + `src/components/Topbar.vue` — navigation
11. Phase 7 (GCal) can start independently after step 3

---

## Key Design Decisions

**`plannedFor` is a standard relation.** It uses the same `Relation` class, `RelationDriver`, and `ItemController` machinery as `mainRelation`. No special-casing in the storage layer is needed; the existing cycle detection, type validation, and ordering infrastructure apply automatically.

**Virtual time-bucket IDs.** Days, weeks, and months are not stored as database documents; their IDs are deterministic computed strings. `ItemController` must handle gracefully a parent ID that has no corresponding document.

**No moment.js.** Use the native `Intl.DateTimeFormat` API. ISO week arithmetic is ~15 lines and does not justify a dependency.

**No implicit cache invalidation.** Vue 3 reactivity via `ReactiveStorage.indexes` makes manual invalidation unnecessary — column contents update automatically.

**Deterministic IDs eliminate races.** Bucket IDs are computed from the date, so concurrent writes are safe and upserts are idempotent.

**Reuse existing components.** `ItemCard`, `ElementList`, `ActionMenu`, and `BaseMenu` are already built. The calendar view composes them rather than reimplementing item rendering.

**Layout persistence in PouchDB.** Store the `meta.calendar-layout` document via the new app's storage abstraction, keeping preferences in sync across sessions and devices.

---

## Open Questions

1. **Add-item in calendar sections**: Creating a task from a calendar section also needs a `builtin.elemOf` parent. What is the default list? Options: a user-configurable default, the most recently used list, or a prompt. Needs a UX decision before Phase 4.

2. **Backlog query**: The backlog column shows all tasks with no `plannedFor` relation. This is not a standard `getChildren` call — `ReactiveStorage` may need a `getUnscheduled()` helper that scans items without a given relation key. Needs investigation before Phase 4.

3. **Repeat-on-done trigger point**: The `markDone` path in the new app needs to be identified before Phase 3 Step 3. If `doneAt` is set via a relation update rather than a direct field write, the trigger point for creating the next recurrence may differ from the old app.

4. **Date library**: The new app has no date library. Native `Intl` covers the formatting requirements, but if `date-fns` is already in `package.json` it is a reasonable alternative. Decide before Phase 2.

5. **Column layout order**: The old app persists column order in the database. Decide whether the new app should use the same `meta.calendar-layout` document (consistent with other settings) or localStorage (simpler for a first version).
