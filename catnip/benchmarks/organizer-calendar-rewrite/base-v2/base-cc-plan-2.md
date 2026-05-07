# Time-Based Planning: Implementation Plan for new-app

## Context

The `old-app` is a Django + Vue 2 TODO application with a rich set of time-based planning features.
The `new-app` is a Vue 3 + TypeScript rewrite with a cleaner domain model, PouchDB storage, and a
relation-based architecture — but it currently has no time-based planning features.

This plan describes how to reimplement those features in `new-app`, taking advantage of the new
architecture rather than porting code verbatim.

---

## Features to Implement

### 1. Time-Based Scheduling (plannedFor)
Items can be assigned to a time bucket: a specific day, ISO week, or calendar month. This is the
core of the planning system. Items without a bucket sit in an unscheduled "backlog".

### 2. Time Board View
A calendar-style board with columns for past/present/future time buckets. The user sees their items
grouped by when they plan to do them, and can drag items between columns.

### 3. Recurring Tasks
A task can be given a repeat interval (e.g., every 2 weeks). When the task is marked done, the
system automatically creates (or moves) the next occurrence to the appropriate future time bucket.

### 4. Date Picker / Quick Scheduling
A date selection UI (dialog or popover) that lets the user pick a specific date or use quick
shortcuts ("this week", "next week", "next month", "in 2 months", etc.).

---

## Architecture Decisions

### Time buckets as first-class items
In `old-app`, days/weeks/months are virtual — they're just string keys (`plannedFor.parentKey`).
In `new-app`, use the existing item+relation system: create **time bucket items** of new types
(`builtin.day`, `builtin.week`, `builtin.month`) that are auto-created on demand and referenced via
a new `builtin.plannedFor` relation.

Benefits:
- Consistent with how lists already work.
- Ordering (mudder-based `seq`) works out of the box.
- Drag-and-drop between buckets is a relation move, the same as moving between lists.
- No special-casing needed in the storage or relation layer.

### Time bucket IDs
Bucket IDs encode their date so they're deterministic and human-readable:
- Day: `time.day:2026-05-08`
- Week: `time.week:2026-W19`
- Month: `time.month:2026-05`

This lets the app find or create a bucket without a database lookup first.

### Repeat logic lives in item-controller
The repeat trigger (on task done) is handled in `item-controller.ts`, not in a component. This
keeps the domain logic testable and decoupled from the UI.

---

## Phase 1 — Domain Layer

**Files to create/edit:**
- `src/domain/types.ts` — add new builtin types and relations
- `src/domain/item.ts` — add `repeat` and `dur` optional properties
- `src/domain/time-utils.ts` — new file: date math and formatting helpers

### 1.1 New builtin types

```typescript
// in BuiltinTypes
timeBucketDay:   "builtin.day",
timeBucketWeek:  "builtin.week",
timeBucketMonth: "builtin.month",
```

### 1.2 New builtin relation

```typescript
// in BuiltinRels
plannedFor: "builtin.plannedFor",
```

This is an ordered single-parent relation (same mechanics as `elemOf`). An item has at most one
`plannedFor` placement at a time.

### 1.3 Item properties

```typescript
interface RepeatConfig {
  increment: number;
  unit: "day" | "week" | "month" | "year";
}

// Added to BaseDoc (optional)
repeat?: RepeatConfig;
dur?: number;        // duration in 15-minute increments, for timed events
```

### 1.4 time-utils.ts

Pure functions, no framework dependencies, easy to unit test.

Key functions:
- `bucketIdForDate(date, granularity)` → deterministic bucket `_id`
- `bucketLabelForDate(date, granularity)` → display string ("Today", "This week", "May 2026", …)
- `parseBucketId(id)` → `{ granularity, date }`
- `bucketDateRange(id)` → `{ start: Date, end: Date }`
- `isPast(bucketId)`, `isPresent(bucketId)`, `isFuture(bucketId)`
- `calcRepeatDate(from: Date, repeat: RepeatConfig)` → next occurrence Date
  - If the result is in the past, keep stepping forward until it's in the future.
- `formatRelativeLabel(date)` → "Today", "Tomorrow", "Yesterday", weekday name, or absolute

Use the native `Temporal` API (or `Intl` + `Date`) rather than moment.js, since moment is not in
`new-app`'s dependencies and is effectively deprecated.

---

## Phase 2 — Storage & Controller Layer

**Files to edit:**
- `src/implementation/reactive-storage.ts` — ensure bucket items can be queried efficiently
- `src/item-controller.ts` — add time-scheduling operations and repeat handling

### 2.1 Bucket auto-creation

Add a `getOrCreateBucket(granularity, date)` helper to `item-controller.ts`. It checks if the
bucket item exists (by deterministic ID) and creates it if not. This keeps the storage clean — only
buckets that have been used are persisted.

### 2.2 Scheduling operations

New methods on `ItemController`:

```typescript
// Assign item to a time bucket (creates bucket if needed)
scheduleItem(itemId: string, granularity: Granularity, date: Date): Promise<void>

// Remove item from its time bucket (moves to backlog)
unscheduleItem(itemId: string): Promise<void>

// Move item to a different bucket
rescheduleItem(itemId: string, granularity: Granularity, date: Date): Promise<void>

// Set/update/remove repeat config
setRepeat(itemId: string, repeat: RepeatConfig | null): Promise<void>
```

### 2.3 Repeat handling

Extend the existing `setDone(itemId)` method in `item-controller.ts`:

```typescript
// After marking done, if item has repeat config:
// 1. Compute next occurrence date via calcRepeatDate()
// 2. Create a new task item (copy text, type, repeat config)
// 3. Schedule new task in the computed future bucket
// 4. Do NOT reschedule the completed item — leave it done where it is
```

This approach (create new item rather than move) keeps the done item as a record and gives the new
occurrence its own history.

### 2.4 Querying items by bucket

Add a reactive query to `reactive-storage.ts`:

```typescript
itemsForBucket(bucketId: string): Reactive<Item[]>
```

Since `new-app` already wraps PouchDB with Vue reactivity, this follows the same pattern as
existing list queries. Index on `relations["builtin.plannedFor"]` keys.

---

## Phase 3 — Time Board Component

**Files to create:**
- `src/views/TimeBoardView.vue` — route-level view
- `src/components/TimeBucket.vue` — a single column (day, week, or month)
- `src/components/TimeBoardSettings.vue` — visibility controls
- `src/composables/useTimeBuckets.ts` — composable that generates the list of visible buckets

### 3.1 Board layout

The board renders a horizontal list of bucket columns. Each column is a `TimeBucket` that shows
items in that bucket using the existing `ItemList` component. A "Backlog" column at the end shows
unscheduled items.

Column categories: past (collapsed by default) | today/this-week | near future | far future | backlog.

### 3.2 useTimeBuckets composable

```typescript
// Returns the ordered list of bucket descriptors to render
function useTimeBuckets(settings: TimeBoardSettings): ComputedRef<BucketDescriptor[]>

interface BucketDescriptor {
  id: string;
  granularity: "day" | "week" | "month";
  date: Date;
  label: string;
  relativePosition: "past" | "present" | "future";
}
```

Generates buckets based on today's date and settings (how many days/weeks/months back and forward to
show). Buckets with no items are still shown in the configured window; they just appear empty.

### 3.3 Drag and drop

Reuse whatever drag-and-drop mechanism `new-app` already uses (or add one). A drag from one
`TimeBucket` to another calls `rescheduleItem()`. A drag to the backlog column calls
`unscheduleItem()`.

### 3.4 Board settings

Settings stored in local storage (not PouchDB — they're device-level preferences):
- Show/hide individual granularities (days, weeks, months)
- How many past days/weeks/months to show
- How many future days/weeks/months to show

---

## Phase 4 — Date Picker / Quick Schedule UI

**Files to create:**
- `src/components/DatePicker.vue` — reusable date selection popover/dialog

### 4.1 Quick schedule buttons

The picker should offer:
- Unschedule (remove from time planning)
- Today / This week / This month
- Tomorrow / Next week / Next month
- In 2 weeks / In 3 weeks / In 2 months (configurable shortcuts)
- Custom date — opens a calendar grid

### 4.2 Granularity selection

The user should be able to choose whether to schedule at day, week, or month granularity. A day-level
assignment shows a specific date chip; a week-level shows "W19"; a month-level shows "May".

### 4.3 Integration points

- `ItemCard.vue` — show a date chip if the item is scheduled; clicking it opens `DatePicker`
- `ActionMenu.vue` — "Schedule" action that opens `DatePicker`

---

## Phase 5 — (Optional) Google Calendar Integration

Defer this phase. The feature exists in `old-app` but is complex (OAuth2, bidirectional sync,
conflict resolution). It is not core to the planning UX and can be added later as a standalone
integration.

When implemented:
- OAuth2 flow via Google Identity Services (same approach as old-app)
- Import: pull GCal events into `new-app` as `builtin.task` items with `dur` set
- Export: push `new-app` tasks to GCal as all-day events, using task `_id` as a stable external ID

---

## Implementation Order

| Step | What | Why first |
|------|------|-----------|
| 1 | `time-utils.ts` | Pure functions, no deps, easy to test in isolation |
| 2 | Domain types (`builtin.day/week/month`, `builtin.plannedFor`) | Everything else depends on these |
| 3 | `getOrCreateBucket` + scheduling methods on controller | Core data operations |
| 4 | Repeat logic in `setDone` | Extends step 3 |
| 5 | `DatePicker.vue` + chip in `ItemCard` | User-facing entry point for scheduling |
| 6 | `useTimeBuckets` composable | Powers the board |
| 7 | `TimeBucket.vue` + `TimeBoardView.vue` | Full calendar view |
| 8 | `TimeBoardSettings.vue` + local storage persistence | Polish |
| 9 | Google Calendar integration | Optional, standalone |

---

## Key Files Reference

**Old-app source of truth:**
- `old-app/frontend/js/time-utils.js` — date math, formatting, `calcRepeatDate`
- `old-app/frontend/js/db-utils.js` — repeat lifecycle (`handleRepeatingTask`, `addTaskRepeat`)
- `old-app/frontend/js/components/time-board.vue` — calendar UI pattern
- `old-app/frontend/js/components/date-dialog.vue` — date picker pattern

**New-app integration points:**
- `new-app/src/domain/types.ts` — add new builtins here
- `new-app/src/domain/item.ts` — add `repeat`, `dur` fields
- `new-app/src/item-controller.ts` — add scheduling + repeat methods
- `new-app/src/implementation/reactive-storage.ts` — add bucket query
- `new-app/src/components/ItemCard.vue` — add date chip
- `new-app/src/components/ActionMenu.vue` — add schedule action
