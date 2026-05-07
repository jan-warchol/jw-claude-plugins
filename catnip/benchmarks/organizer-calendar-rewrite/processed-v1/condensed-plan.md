# Calendar & Time-Based Planning: Condensed Plan

## New App Architecture

Relations are the core abstraction with three layers: **RelationController** (`relations.ts`) validates constraints; **RelationDriver** (`relation-driver.ts`) handles mudder-based sequence math; **ItemController** (`item-controller.ts`) orchestrates and persists. `ReactiveStorage` maintains a Vue-reactive `(relationKey, parentId)` index — calendar views read from it without extra queries.

## Architecture Decision

Schedule tasks via a `builtin.plannedFor` relation whose parent IDs are synthetic date strings, not stored documents. The existing index works identically for virtual parents; no new infrastructure needed. A task holds a list parent (`elemOf`) and a scheduled date independently.

Synthetic ID format: `day:YYYY-MM-DD`, `week:YYYY-WNN` (ISO), `month:YYYY-MM`. Relation config: ordered, single-parent, not required. `ItemController` must handle gracefully a parent ID with no corresponding document.

## Data Model

**`src/domain/types.ts`** — add `plannedFor` to `BuiltinRels`; `Granularity = 'day'|'week'|'month'`; `ScheduleTarget = { granularity, date } | { granularity: 'backlog' }`.

**`src/domain/item.ts`** — `scheduledFor: ScheduleTarget | null` getter; `repeat?: { increment: number; unit: Granularity }`.

**`src/domain/relations.ts`** — register `builtin.plannedFor` config.

**`src/domain/time-utils.ts`** *(new)* — `bucketId`, `parseBucketId`, `formatBucketLabel`, `formatBucketSubheader`, `timeStatus`, `prevBucket`/`nextBucket`, `bucketContains`, `iteratePeriods`, `advanceByRepeat`. Native `Intl` only; no moment.js.

## Scheduling (`src/item-controller.ts`)

Add `scheduleTo`, `unschedule`, `bulkScheduleTo`, `setRepeat`. On `markDone`, auto-advance `plannedFor` by `repeat` interval if set.

## UI Components

| Component | Notes |
|---|---|
| `views/CalendarView.vue` | Route `/calendar`; manages columns, past/future window sizes, midnight date refresh; layout persisted to `meta.calendar-layout` (PouchDB); column list is a reactive `ColumnDescriptor[]` |
| `components/TimeBucketColumn.vue` | Primary + secondary label, past/current/future styling, collapsed empty-section badge, HTML5 drag-drop; "Add item" pre-sets `plannedFor` |
| `components/CalendarColumnNav.vue` | Show more / Show previous with progressive doubling; auto-expands past window when overdue tasks exceed it |
| `components/CalendarSettings.vue` | Toggle column types, custom lists, column-width ratios; persists to `meta.calendar-layout` |
| `components/DateMenu.vue` | Today / Tomorrow / This week / Next week / This month / Remove / Other; single and bulk mode |
| `components/DatePickerDialog.vue` | `<dialog>` + `showModal()`; relative shortcuts, `<input type="date">` with week/month granularity switch |

Modify: `ItemCard.vue` + `ItemHeader.vue` (date chip, opens `DateMenu`); `ActionMenu.vue` (add "Schedule…" and "Set repeat…"). Google Calendar sync deferred.

## Implementation Order

1. `time-utils.ts`
2. Domain: types, relations, item
3. `ItemController` scheduling methods
4. `TimeBucketColumn` + `CalendarView` (read-only first)
5. `CalendarColumnNav`
6. `DateMenu` + `DatePickerDialog`; wire chip into cards and `ActionMenu`
7. Drag-and-drop
8. `CalendarSettings`; router + Topbar

## Key Design Decisions

Virtual parent IDs reuse existing infrastructure without schema changes. No moment.js — native `Intl`. Vue 3 reactivity via `ReactiveStorage.indexes` eliminates manual cache invalidation. Deterministic IDs make concurrent upserts safe. Reuse existing `ItemCard`, `ElementList`, `ActionMenu`, `BaseMenu` — calendar view composes, not reimplements.

## Open Questions

1. **Default list** — which `elemOf` parent is assigned when creating a task from a calendar section?
2. **Backlog query** — items with no `plannedFor` need a `getUnscheduled()` helper; `getChildren` does not work.
3. **Repeat trigger** — identify the `markDone` hook before implementing recurrence; if `doneAt` is set via a relation update the trigger point differs.
4. **Column order persistence** — `meta.calendar-layout` (consistent) vs localStorage (simpler)?
