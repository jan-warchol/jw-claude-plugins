# Plan: Time-Based Planning Features in new-app

## Overview

The old-app has a mature time-based planning system: tasks can be planned for a specific day, week, or month; a calendar board renders multiple time scales side-by-side; and recurring tasks automatically reschedule when completed. The new-app has a clean domain-driven architecture with TypeScript, Vue 3, and an extensible relation/type registry — but no time-based features yet.

This plan adds time-based planning to new-app by extending its existing domain and registry system rather than porting old-app code verbatim.

---

## How the Old System Works (Reference)

- `plannedFor` is a parent pointer stored on each task: `{ parentClass, parentKey, seq }` where `parentClass` is `"day" | "week" | "month" | "list"` and `parentKey` is an ISO string (e.g. `"2024-05-08"`).
- Days, weeks, and months are not stored as items in the DB — they are virtual containers computed on the fly from the `parentKey` string.
- The time board (`time-board.vue`) renders columns: a list of days, a list of weeks, a list of months, and optionally custom lists/backlog. Each column shows tasks planned for that period.
- Recurring tasks store a `repeat` config. When a task is marked done, the app computes the next occurrence and creates a duplicate.

---

## Proposed Approach for new-app

Rather than duplicating the old-app's ad-hoc `parentClass + parentKey` approach, we can model time periods as **real items** in PouchDB. A `builtin.day` item with `_id` derived from its ISO date is a natural container for tasks. This fits the existing `builtin.elemOf` relation pattern and lets us reuse `getChildren()`, ordering, and the existing `BasicView` rendering for free.

```
meta.root
└── [builtin.itemType: "Days"]    (like existing "Tasks", "Lists", etc.)
    ├── builtin.day  "2024-05-08"
    │     ├── builtin.task  "Buy milk"
    │     └── builtin.task  "Call doctor"
    └── builtin.day  "2024-05-09"
          └── builtin.task  "Team meeting"
```

Weeks and months are optional grouping containers for tasks that don't need a specific day. A separate `builtin.week` / `builtin.month` type can exist alongside `builtin.day`.

### Why this is better than the old approach

| Old-app | New-app plan |
|---|---|
| Virtual containers computed from string keys | Real items — consistent with existing model |
| Separate `plannedFor` relation + seq | Reuses existing ordered `builtin.elemOf` relation |
| Custom reactive-cache derived views | Reuses `getChildren()` + existing reactivity |
| Day/week/month container code spread across multiple files | Isolated in domain layer with one new file each |

---

## Implementation Steps

### Step 1 — Add Time-Period Item Types

**File:** `src/domain/item.ts`

Extend `BuiltinTypes` with:
```typescript
"builtin.day"   // ISO date key  e.g. "2024-05-08"
"builtin.week"  // ISO week key  e.g. "2024-W19"
"builtin.month" // ISO month key e.g. "2024-05"
```

Each type:
- Allows `builtin.task` and `builtin.note` as children (via `allowedChildTypes`)
- Has a deterministic `_id` derived from its key (e.g. `day:2024-05-08`) so we never create duplicates — we upsert
- Is never "done" or "trashed" (no `doneAt`)
- Inherits no color by default (color can be set per day if desired)

**No new relation needed** — these items use the existing `builtin.elemOf` to hold children.

A helper is needed to get-or-create a time period item:

```typescript
// item-controller.ts
async getOrCreateDay(isoDate: string): Promise<Item>
async getOrCreateWeek(isoWeek: string): Promise<Item>
async getOrCreateMonth(isoMonth: string): Promise<Item>
```

This upserts a day/week/month item and ensures it exists under the correct parent `itemType` container.

---

### Step 2 — Time Utilities

**New file:** `src/time-utils.ts`

Pure functions, no Vue or PouchDB dependency:

```typescript
todayISO(): string                          // "2024-05-08"
isoWeekOf(date: Date): string              // "2024-W19"
isoMonthOf(date: Date): string             // "2024-05"

formatDay(isoDate: string): string         // "Today", "Tomorrow", "Mon 5 May"
formatWeek(isoWeek: string): string        // "This week", "Next week", "W19 · 6–12 May"
formatMonth(isoMonth: string): string      // "May 2024"
formatDateChip(isoDate: string): string    // Short label for task cards: "Today", "Tue"

periodStatus(key: string): "past" | "present" | "future"
  // used to dim past periods and highlight the present

nextRepeatDate(
  currentKey: string,
  periodType: "day" | "week" | "month",
  increment: number,
  unit: "day" | "week" | "month" | "year"
): string
```

Week arithmetic must handle ISO week numbering (weeks start Monday, week 1 is the week containing the year's first Thursday). Use `date-fns` or `temporal-polyfill` rather than `moment.js`, keeping the bundle small.

---

### Step 3 — Time Board View

**New file:** `src/views/TimeBoardView.vue`

A new top-level route (`/time`) showing the planning calendar.

#### Layout

Three columns side by side (similar to old-app's time board):

```
┌──────────┬────────────┬────────────┐
│  Days    │   Weeks    │  Months    │
│──────────│────────────│────────────│
│ Yesterday│            │            │
│  ·task A │  Last week │  Last month│
│          │  ·task B   │            │
│──────────│────────────│────────────│
│ Today ★  │  This week │  This month│
│  ·task C │  ·task D   │  ·task E   │
│  [+ add] │  [+ add]   │  [+ add]   │
│──────────│────────────│────────────│
│ Tomorrow │  Next week │  Next month│
│──────────│────────────│────────────│
│ Tue      │  Week+2    │  Month+2   │
│ ...      │  ...       │  ...       │
└──────────┴────────────┴────────────┘
```

#### Sections

Each column renders a scrollable list of period sections. A section contains:
- Period header with formatted label and pending-task count badge
- `ElementList` of tasks for that period (reused existing component)
- Inline "Add task" input (reused `AddItem` component)

Past periods with no pending tasks are collapsed by default. The current period is always visible and highlighted. Future periods are shown for a configurable window (e.g. 14 days, 8 weeks, 6 months) with a "Show more" button.

#### Column visibility

Configurable via a settings panel (persisted to `localStorage`), similar to old `time-board-settings.vue`. Users can hide the Weeks or Months column.

---

### Step 4 — Date Picker / Schedule Dialog

**New file:** `src/components/ScheduleDialog.vue`

Triggered from a task's context menu or action button. Shows:

- Quick options: Today, Tomorrow, This week, Next week, This month, Next month
- A mini calendar picker for precise day selection
- "No date" option to unschedule

On selection, the dialog calls:
```typescript
controller.moveToPeriod(item, targetPeriodItem)
```

Which removes the item from its current time-period parent and appends it to the target period item (using existing `replaceParents` or `append` logic on `builtin.elemOf`).

The button to open this dialog is surfaced on `ItemCard` and `ItemHeader` as a date chip (showing the current scheduled period if any, using `formatDateChip()`).

---

### Step 5 — Recurring Tasks

**Data model extension** — add optional `repeat` field to `Item`:

```typescript
interface RepeatConfig {
  increment: number       // e.g. 2
  unit: "day" | "week" | "month" | "year"
}
```

Stored directly on the item doc: `item.repeat = { increment: 1, unit: "week" }`.

**Logic in `item-controller.ts`:**

Extend `toggleDone()`:
```typescript
async toggleDone(item: Item): Promise<void> {
  // existing done logic ...
  if (item.repeat && item.done) {
    await this.scheduleNextRecurrence(item)
  }
}

private async scheduleNextRecurrence(item: Item): Promise<void> {
  const currentPeriod = this.getMainParent(item)  // day/week/month item
  const nextKey = nextRepeatDate(currentPeriod.text, ...)
  const nextPeriod = await this.getOrCreateDay(nextKey)  // or week/month
  // Clone the item without doneAt, place in nextPeriod
  await this.addChild(nextPeriod, { text: item.text, repeat: item.repeat })
}
```

Guard: if a pending (not done) sibling with the same text already exists in the computed next period, skip creating a duplicate (same logic as old-app's `repeated` flag, but checked structurally rather than via a flag).

**UI:** A "Repeat" toggle in the task edit panel, with increment and unit selectors. Only shown when the task is scheduled to a time period (unscheduled tasks cannot have a repeat).

---

### Step 6 — Router Integration

**File:** `src/router/index.ts`

Add route:
```typescript
{ path: "/time", component: TimeBoardView }
```

Add a nav link in the root layout alongside the existing item-type navigation.

---

### Step 7 — Backlog / Unscheduled Tasks

Tasks without any time-period parent are "unscheduled". A fourth optional column in the time board can show these. They are simply all tasks whose sole `builtin.elemOf` parent is a non-time-period container (i.e. a plain `builtin.list`).

Alternatively, a dedicated `builtin.list` called "Backlog" (created on first use) serves as an explicit landing zone for unscheduled tasks, consistent with the existing list architecture.

---

## What We Are Not Porting

| Old-app feature | Decision |
|---|---|
| PouchDB ↔ CouchDB sync | Out of scope (new-app is local-only for now) |
| Multi-user / assignee filtering | Out of scope |
| Django authentication backend | Out of scope |
| Custom list colors | Already supported by existing `color` field |
| Label-based filtering | Already supported by existing `builtin.labels` relation |
| `mudder` seq reordering | Already in new-app's `relation-driver.ts` |

---

## File Summary

| File | Status | Notes |
|---|---|---|
| `src/domain/item.ts` | Modify | Add `builtin.day`, `builtin.week`, `builtin.month` types; add `repeat` field |
| `src/time-utils.ts` | New | Pure time formatting and calculation functions |
| `src/views/TimeBoardView.vue` | New | Main calendar board |
| `src/components/ScheduleDialog.vue` | New | Date picker / schedule dialog |
| `src/components/TimePeriodSection.vue` | New | Single period section (header + task list + add) |
| `src/item-controller.ts` | Modify | `getOrCreateDay/Week/Month`, `moveToPeriod`, recurrence logic in `toggleDone` |
| `src/router/index.ts` | Modify | Add `/time` route |
| `src/presentation.ts` | Modify | Date chip formatting helpers for `ItemCard`/`ItemHeader` |

---

## Dependency

Add `date-fns` (already a common dependency, tree-shakeable) or use the native `Temporal` API (available in modern browsers) for ISO week arithmetic. Avoid adding `moment.js` — it is large and the old-app only used it for week calculations.
