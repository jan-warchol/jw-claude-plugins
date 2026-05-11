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
- Past sections are collapsed; current section always visible; future sections expandable
- "Show previous" / "Show more" controls reveal additional sections progressively
- Section headers show relative labels ("Today", "This week") near the present
- Task cards display a compact date chip from their `plannedFor` assignment
- Scheduling submenu in `ActionMenu` offers: Today, Tomorrow, This week, Next week, This month, Backlog, Remove date, Other date
- Currently assigned slot is disabled in the scheduling submenu
- Tasks with a `repeat` property auto-reschedule when marked done
- The `plannedFor` relation reuses the existing `mudder`-based `seq` ordering

## Non-Goals / Out of Scope

- Custom list columns or per-list grouping within time slots
- Drag-and-drop rescheduling
- Column visibility settings dialog
- Google Calendar integration

## Dependencies & Setup

- No new npm packages — native `Date` and `Intl.DateTimeFormat` cover all formatting
- Add `builtin.plannedFor` to `BuiltInRelationsConfig` in `src/domain/relations.ts`
- Add `builtin.timeSlot` type to `BuiltInTypesConfig` with `childRelation: builtin.plannedFor` and `allowedChildTypes: [builtin.task]`
- Add `backlog` virtual item to `seedItems` in `src/domain/item.ts`

## Implementation Steps

### 1. Domain: relation and type definitions
Add `builtin.plannedFor` and `builtin.timeSlot` to their registries. Add `backlog` seed item.

### 2. Virtual time-slot items (`src/domain/time-slots.ts`)
- `parseSlotID(id)` → `{ unit, date }` or null
- `makeSlotItem(id)` → virtual `Item` with correct `allowedChildTypes`
- `slotIDForDate(unit, date)` → canonical ID string
- Date helpers: `startOfWeek`, `startOfMonth`, range iteration

Extend `PouchProxy.getItem()` to intercept date-pattern IDs and return `makeSlotItem()`.
`getChildren()` already works — `indexes` auto-populates as tasks store date IDs.

### 3. Time formatting (`src/utils/time-utils.ts`)
Pure functions using native `Date`: `formatDayRelative`, `formatWeek`, `formatMonth`,
`formatDateChip`, `pastOrFuture`, `calcRepeatDate`.

### 4. Scheduling submenu
Create `src/components/ScheduleMenu.vue`. Add to `ActionMenu.vue` as a sub-menu.
Disables the currently assigned slot; calls `$itemController.replaceParents(...)`.

### 5. Date chip on task cards
Add `plannedForChip` computed to `ItemHeader.vue` via `formatDateChip`. Render as a
small badge; hidden when no `plannedFor` is set.

### 6. Repeat logic
Store `repeat: { increment: number; unit: 'day'|'week'|'month' }` on items. Extend
`ItemController.toggleDone()` to reschedule via `replaceParents` when `item.repeat` exists.
Add "Set repeat" to `ActionMenu`.

### 7. TimeBoard view
Create `src/views/TimeBoard.vue` and `src/components/TimeBoardColumn.vue`. Columns hold
`pastCount`/`futureCount` state, iterate slots from `time-slots.ts`, render `ItemList` per slot.

### 8. Router and navigation
Add `{ path: '/time', component: TimeBoard }` to `src/router/index.ts`. Link in `Topbar.vue`.

## Risks & Assumptions

- **Index timing**: `indexes` fills during `init()`; `TimeBoard` sees empty arrays first,
  then reactive updates — verify visually.
- **Type validation**: `makeSlotItem()` must include `builtin.task` in `allowedChildTypes`
  or `Relation.ensureInsertAllowed` will reject scheduling.
- Assumes each task has at most one `plannedFor` parent.

## Alternatives Considered

- **Persisted time-slot documents**: bloats PouchDB, requires cleanup — rejected.
- **Preserve parentClass/parentKey encoding**: bypasses relation architecture — rejected.
- **date-fns**: no benefit over native `Date`/`Intl` for this use case — rejected.

## Testing

- Manually: schedule a task to Today → appears in Days column; mark repeating task done
  → reschedules; remove date → disappears from board.
- Unit-test `time-utils.ts` pure functions.
- Unit-test `calcRepeatDate` edge cases: past dates snap to today, week/month alignment.
