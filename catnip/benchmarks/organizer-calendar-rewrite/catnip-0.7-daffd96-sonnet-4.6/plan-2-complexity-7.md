---
goal: Add time-based task scheduling and calendar board to new-app
prompt: "There are two directories in this project:\n- `old-app` with a legacy codebase for a TODO web application\n- `new-app` with a rewrite of the same application using newer version of the framework, better architecture etc.\n\nI want to reimplement time-based planning features in the new version.\nIt should behave similarly (not necessarily the same) to the old one but take advatage of the new, better architecture. complexity: 7"
complexity: 7
project: /home/jan/workspaces/catnip-test/org-rewrite/new-app
model: claude-sonnet-4-6
---

## Problem Statement

The new app cannot schedule tasks to time periods (day, week, month) or a backlog, and has no calendar board view. The old app's `plannedFor` used a non-standard `parentClass + parentKey` pair outside the Item system. The reimplementation must fit the new app's relation-centric TypeScript architecture.

## Design Decisions

- **Virtual date Items** (`day:2025-05-11`, `week:2025-05-05`, `backlog`): synthetic Items generated on demand, never persisted, so `getChildren()` works via the existing index
- **`builtin.scheduledFor`**: new single-parent, unordered relation; assigning a new date automatically replaces the previous slot
- **Explicit backlog**: items without `scheduledFor` are invisible in the time board; backlog requires explicit assignment

## Success Criteria

- Task can be scheduled via ActionMenu: Today, Tomorrow, This week, Next week, Backlog
- Scheduling to a new date replaces the previous `scheduledFor`
- Tasks appear in the Days column under the correct date section
- Tasks appear in the Weeks column under the correct ISO week
- Backlog column shows only explicitly assigned items
- Items with no `scheduledFor` do not appear in the time board
- Sections display past / current / future styling
- Each column has show-more and show-previous navigation
- A date chip appears on scheduled items in regular list views
- Completing a repeating task auto-reschedules it to the next date
- Virtual date Items are never stored in `PouchProxy.items`
- `getChildren('day:2025-05-11')` returns correctly scheduled tasks
- The `/time` route renders TimeBoardView

## Non-Goals

- Calendar column visibility settings dialog
- Custom date picker (calendar widget) or quick-picks like "in 2 weeks"
- Multi-user / multi-DB backlog separation
- Months column (defer to later iteration)

## Dependencies / Setup

- `meta.timeSlot` type registered in `ItemTypeRegistry` at init with `allowedChildTypes: [task, note]`
- `builtin.scheduledFor` added to `BuiltinRels` and `BuiltInRelationsConfig` (single-parent, unordered)
- `PouchProxy.getItem()` extended to generate virtual Items for date-pattern IDs
- `/time` route added to Vue Router

## Implementation Phases

### Phase 1 — Domain
- Add `builtin.scheduledFor` to `types.ts` and `relations.ts`
- Add `meta.timeSlot` to `BuiltinTypes`, register during `init()` before seed items
- Extend `PouchProxy.getItem()`: detect `day:*`, `week:*`, `backlog` IDs; return read-only virtual Item without storing it

### Phase 2 — Time utilities (`src/domain/time-utils.ts`)
- `parseTimeSlotID(id)` → `{ granularity, date } | null`
- `makeTimeSlotID(granularity, dateString)` → slot ID
- `todaySlots(now)` → `{ todayID, tomorrowID, thisWeekID, nextWeekID }`
- `formatSectionLabel(slotID, now)` → "Today", "Mon 12 May", "12–18 May"
- `pastOrFuture(slotID, now)` → `'past' | 'current' | 'future'`
- `calcRepeatDate(item, now)` → next ISO date string or null

### Phase 3 — ItemController
- `getScheduledSlot(item)` → `slotID | null`
- `scheduleTo(items, slotID)` → `replaceParents` on `scheduledFor`
- `unschedule(item)` → `clearRelation(item, scheduledFor)`
- Extend `toggleDone()`: call `scheduleTo(calcRepeatDate(item))` when repeat data present

### Phase 4 — TimeBoardView
- `TimeBoardView.vue` at `/time`: renders TimeColumn for days, weeks, backlog
- `TimeColumn.vue`: owns `futureSections`/`pastSections` counters, show-more/show-previous
- `TimeSection.vue`: receives `slotID`, calls `store.getChildren`, applies past/current/future class

### Phase 5 — Scheduling UI
- `ScheduleMenu.vue`: Today / Tomorrow / This week / Next week / Backlog / Remove; disables current slot
- Integrate into `ActionMenu.vue`; add `DateChip.vue` to `ItemCard.vue`

## Error Handling

- `PouchProxy.getItem()` returns `null` for malformed date IDs rather than throwing
- Repeat-reschedule failure logs a warning but does not block the done-toggle

## Security

No server-side changes. Virtual item generation does not evaluate user input as code.

## Performance

- `getChildren(slotID)` is O(1) via existing `PouchProxy` index — no extra queries
- TimeBoardView renders only the current `futureSections`/`pastSections` window

## Alternatives Considered

- **Direct fields** (`scheduledDate`, `scheduledGranularity`): simpler but bypasses the relation system and its O(1) index
- **Persisted date Items**: cleaner semantically but generates orphan documents in PouchDB over time

## Risks and Assumptions

- `meta.timeSlot` must be registered before seed items so type validation passes on scheduling
- Components must call `getItem()` not access `PouchProxy.items`; virtual Items are absent from the map
- `todaySlots()` must be called fresh per action to avoid midnight staleness in long-running sessions
- `Relation.ensureInsertAllowed()` must accept task/note as children of the virtual `meta.timeSlot` type

## Testing

- Unit-test `time-utils.ts`: `pastOrFuture`, `formatSectionLabel`, `calcRepeatDate` with fixed `now`
- Unit-test `PouchProxy.getItem()`: valid date IDs return virtual Items; invalid IDs return `null`
- Unit-test `ItemController.scheduleTo()`: `scheduledFor` set, previous slot cleared
- Manual: schedule task to Today → appears in TimeBoardView; complete repeating task → auto-reschedules
