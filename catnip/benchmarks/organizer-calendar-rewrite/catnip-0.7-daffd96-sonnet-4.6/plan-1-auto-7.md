---
goal: Reimplement time-based planning features in new Vue 3 app
prompt: "There are two directories in this project:\n- `old-app` with a legacy codebase for a TODO web application\n- `new-app` with a rewrite of the same application using newer version of the framework, better architecture etc.\n\nI want to reimplement time-based planning features in the new version.\nIt should behave similarly (not necessarily the same) to the old one but take advatage of the new, better architecture."
complexity: 7
project: /home/jan/workspaces/catnip-test/org-rewrite
model: claude-sonnet-4-6
---

## Problem Statement

The old app's `plannedFor` relation identifies time slots via a `parentClass`/`parentKey`
pair stored directly on each task. The new app represents all relation targets as `Item`
objects with string IDs, ordered by `seq`, stored in `PouchProxy`'s reactive `indexes`
map. The challenge is adapting time slots to virtual (non-persisted) items with IDs like
`day:2025-05-11` that fit naturally into the existing `RelationController` and storage
layer, then building the board view and scheduling UI on top.

## Success Criteria

- `builtin.plannedFor` relation: single-parent, ordered, non-required
- Tasks are scheduled by assigning a virtual time-slot item as their `plannedFor` parent
- Virtual items (`day:*`, `week:*`, `month:*`, `backlog`) are never persisted to PouchDB
- `PouchProxy.getItem()` returns generated `Item` objects for date-pattern IDs
- `/time` route renders TimeBoard with Days, Weeks, Months, and Backlog columns
- Past sections collapsed by default; current section always visible; future sections start at 2 (days) or 1 (weeks/months)
- Each click of "show previous" / "show more" reveals progressively more sections: 0→1→3→6→12→…
- Section headers use an icon + label layout matching the `list-header` style; relative labels ("Today", "This week") near the present
- Task cards display a compact date chip from their `plannedFor` assignment; repeat config shown as a chip too
- Repeat config also shown as an editable row in the item detail view (`ItemList`), matching `RelationMenu` style
- Scheduling submenu in `ActionMenu` (not a separate component) offers: Today, Tomorrow, This week, Next week, This month, Backlog, Remove date, Other date; currently assigned slot is disabled
- Completing a repeating task marks it done and creates a duplicate (with all children, recursively) scheduled at the next interval
- The `plannedFor` relation reuses the existing `mudder`-based `seq` ordering
- Items can be added directly from the time board without belonging to a list

## Non-Goals / Out of Scope

- Custom list columns or per-list grouping within time slots
- Drag-and-drop rescheduling
- Column visibility settings dialog
- Google Calendar integration

## Dependencies & Setup

- No new npm packages — native `Date` and `Intl.DateTimeFormat` cover all formatting
- Add `builtin.plannedFor` to `BuiltInRelationsConfig` in `src/domain/relations.ts`
- Add `builtin.timeSlot` type to `BuiltInTypesConfig` with `childRelation: builtin.plannedFor`, `icon: "event"`, and `allowedChildTypes` defaults to `LeafLikeTypes` (`[builtin.task, builtin.note]`)
- `BACKLOG_ID = "backlog"` is defined in `src/domain/time-slots.ts`; the `backlog` seed item in `src/domain/item.ts` uses the string literal directly to avoid a circular import

## Implementation

### Domain: relation and type definitions (`src/domain/`)

**`types.ts`**: Add `timeSlot: "builtin.timeSlot"` to `BuiltinTypes`; `plannedFor: "builtin.plannedFor"` to `BuiltinRels`.

**`relations.ts`**: Add to `BuiltInRelationsConfig`:
```ts
{
  _id: BuiltinRels.plannedFor,
  text: "planned for",
  ordered: true,
  multiparent: false,
  required: false,
  icon: "event",
}
```

**`item.ts`**: Add `timeSlot` to `BuiltInTypesConfig`:
```ts
{ _id: BuiltinTypes.timeSlot, text: "time slot", childRelation: BuiltinRels.plannedFor, icon: "event" }
```
Add `RepeatConfig` type and `repeat?: RepeatConfig` property on `Item` (not enumerable).
Add `backlog` seed item (string literal ID `"backlog"`, type `builtin.timeSlot`).

### Virtual time-slot items (`src/domain/time-slots.ts`)

Exports:
- `BACKLOG_ID = "backlog"`
- `SlotUnit = "day" | "week" | "month"`
- `parseSlotID(id)` → `{ unit, date }` or `{ unit: "backlog" }` or `null`
- `isSlotID(id)` → boolean
- `formatISODate(date)` → `"YYYY-MM-DD"`
- `slotIDForDate(unit, date)` → `"unit:YYYY-MM-DD"`
- `startOfDay`, `startOfISOWeek`, `startOfMonth` — date normalisers
- `addUnits(date, count, unit)` — advances date by N units
- `anchorDate(unit)` — today/this-week-start/this-month-start
- `iterateSlots(unit, pastCount, futureCount)` → array of slot IDs centered on anchor
- `makeSlotItem(id)` → virtual `Item` (type `builtin.timeSlot`, `readOnly` not set, `allowedChildTypes = LeafLikeTypes`)

`PouchProxy.getItem()` is extended to intercept date-pattern IDs and return `makeSlotItem()`. `getChildren()` already works — `indexes` auto-populates as tasks store date IDs.

### Time formatting (`src/utils/time-utils.ts`)

Pure functions using native `Date`:
- `formatDayRelative(date)` — "Yesterday" / "Today" / "Tomorrow" / weekday / "May 12"
- `formatWeek(date)` — "Previous week" / "This week" / "Next week" / "May 5–11"
- `formatMonth(date)` — "Previous month" / "This month" / "Next month" / "May 2026"
- `formatSlotLabel(slotID)` — dispatches to the above; "Unplanned" for backlog
- `formatDateChip(slotID)` — compact chip format: "Today", "Tomorrow", "2026.05.12", "2026.05.12–18", "2026.05"
- `pastOrFuture(slotID)` → `"past" | "current" | "future"` — used to style slot sections
- `calcRepeatDate(repeat, currentSlotID)` — adds the repeat interval; snaps to today if result is in the past; aligns week/month IDs to their canonical start date

### Scheduling submenu

Implemented inline in `ActionMenu.vue` (not as a separate component). A `scheduleOpen`
boolean toggles a sub-list of buttons. Calls `$itemController.replaceParents(...)`. The
"Other date" option uses a hidden `<input type="date">` triggered programmatically.

### Date and repeat chips on task cards (`ItemHeader.vue`)

- `plannedForChip` computed reads `item.relations[BuiltinRels.plannedFor]`, formats via `formatDateChip`; shown as an `event` icon + text badge
- `repeat` chip: `repeat` icon + `"Nd"/"Nw"/"Nm"` abbreviation; shown when `item.repeat` is set
- Both hidden on `list-header` (detail view header) via `.list-header .attributes { display: none }`
- `attributes` computed excludes `mainRelation` and `plannedFor` parents (already shown via dedicated chips)

### Repeat indicator in item detail view (`RepeatAttr.vue`)

A `<tr class="attribute">` component matching `RelationMenu`'s visual style. Shows
`repeat` icon + "Repeat:" label + value ("1 day", "2 weeks" etc.), or "none" in italic
when unset. Clicking opens a `prompt()` to edit. Used in `ItemList.vue`'s `item-attrs`
table, rendered only when `item.actionable`.

### Repeat logic (`ItemController.toggleDone`)

When completing a repeating item that has a `plannedFor` parent:
1. The original is marked done (`doneAt: Date.now()`) in a separate write.
2. A duplicate is created and scheduled at the next slot (`calcRepeatDate`). The original
   and duplicate are different PouchDB documents so there is no `_rev` conflict.

The duplicate is created by `#createRepeatDuplicate`, which:
- Copies `text`, `type`, `repeat`, `color`, `icon` (not `doneAt` or relations)
- Places the duplicate under the same `mainRelation` parents as the original, plus the next slot as `plannedFor` parent
- Recursively copies the entire child subtree: `#copyChildren` traverses `getChildren()` depth-first, creates shallow copies of every descendant, and places each batch of copies under their new parent via `calcUpdateByRelation("add", ...)`
- All new items and their placements are collected and saved in a **single** `bulkUpdate` call

If the repeat has no `plannedFor` parent, or `calcRepeatDate` returns null (e.g., backlog), the item is simply marked done without duplication.

### TimeBoard view

**`src/views/TimeBoard.vue`**: Four `TimeBoardColumn` instances — Days (`day`), Weeks (`week`), Months (`month`), Backlog (`backlog`) — in a horizontal flex layout with `overflow-x: scroll`.

**`src/components/TimeBoardColumn.vue`**:

Props: `unit: SlotUnit | "backlog"`, `title: string`, `icon: string`.

State: `pastCount` (default 0), `futureCount` (default 2 for days, 1 for others), `topExpanded`, `bottomExpanded`.

`slotIDs` computed calls `iterateSlots(unit, pastCount, futureCount)` or returns `[BACKLOG_ID]`.

Each slot section:
- Header: `event` icon + formatted label + child-count badge (matching `list-header` height/padding/icon pattern)
- Status class (`status-past/current/future`) drives opacity: past is tertiary, current is full opacity with bold label, future is secondary
- `ElementList` with `component="ItemCard"` (not `ItemList`)
- `AddItem` component — allows list-less task/note creation directly in the time board; shown when the slot item exists

Navigation bars (top/bottom, hidden for backlog):
- Collapsed state (28px): single full-width icon button with centered arrow (`expand_less` / `expand_more`)
- Expanded state (36px): two side-by-side buttons — "show previous/more" (62% width) and "hide ✕" (36% width)
- Each click of the expand button runs `increaseProgressively(n)`: `0→1, 1→3, n<30→n×2, n≥30→n+30`
- The first click both expands the nav bar and immediately increments the count (sections appear right away)
- "hide" resets count to 0 (top) or initial default (bottom) and collapses the bar

### Router and navigation

`{ path: '/time', component: TimeBoard }` added to `src/router/index.ts`.
`calendar_today` icon button added to `Topbar.vue`.

## Risks & Assumptions

- **Index timing**: `indexes` fills during `init()`; `TimeBoard` sees empty arrays first,
  then reactive updates — acceptable for now, verify visually.
- **Type validation**: `makeSlotItem()` returns items with `allowedChildTypes = LeafLikeTypes`
  so `Relation.ensureInsertAllowed` accepts tasks and notes. The Item constructor defaults
  `childRelationKey` to `mainRelation` when no typeDef is passed; `timeSlotTypeDef` is
  looked up by name to get the correct `plannedFor` childRelation.
- Assumes each task has at most one `plannedFor` parent (single-parent relation).
- Children of a repeated item do NOT inherit `plannedFor` or label relations from the original — only `text`, `type`, `repeat`, `color`, and `icon` are copied.

## Alternatives Considered

- **Persisted time-slot documents**: bloats PouchDB, requires cleanup — rejected.
- **Preserve parentClass/parentKey encoding**: bypasses relation architecture — rejected.
- **date-fns**: no benefit over native `Date`/`Intl` for this use case — rejected.
- **Separate `ScheduleMenu.vue` component**: unnecessary indirection; scheduling is implemented inline in `ActionMenu.vue` — rejected.
- **Move repeating item to next slot** (instead of duplicate): loses history; duplicate pattern preserves the completed original in its original slot — rejected.

## Testing

- Manually: schedule a task to Today → appears in Days column; mark repeating task done
  → original stays (done), duplicate appears in next slot with same children; remove date
  → disappears from board; add task directly in time board without a list → task created
  with only `plannedFor` parent.
- Unit-test `time-utils.ts` pure functions.
- Unit-test `calcRepeatDate` edge cases: past dates snap to today, week/month alignment.
