---
goal: Reimplement time-based planning features in the new Vue 3 app
prompt: There are two directories in this project:
- `old-app` with a legacy codebase for a TODO web application
- `new-app` with a rewrite of the same application using newer version of the framework, better architecture etc.

I want to reimplement time-based planning features in the new version.
It should behave similarly (not necessarily the same) to the old one but take advatage of the new, better architecture.
complexity: 7
project: /home/jan/workspaces/catnip-test/org-rewrite/new-app
model: claude-sonnet-4-6
---

## Context

The old app links tasks to time periods via a `plannedFor` relation (day/week/month). The new app's
storage already indexes children by any relation key — so virtual IDs like `day:2024-01-15` work as
parent IDs without storing DB items per date.

## Features in scope

- Time-board view at `/calendar` (day/week/month columns, prev/next navigation)
- Quick scheduling submenu inside ActionMenu
- Recurring tasks (advance schedule on done)

## Out of scope

Bulk reschedule, Google Calendar integration, duration tracking, multi-user backlogs

## Domain model

### `builtin.scheduledFor` relation

Add to `BuiltInRelationsConfig` in `src/domain/relations.ts`:
`ordered: true`, `multiparent: false`, `required: false`, `icon: 'event'`.
Single-parent semantics mean assigning a new period automatically replaces the previous one.

### Virtual time period IDs

Format: `day:YYYY-MM-DD`, `week:YYYY-MM-DD` (ISO Monday), `month:YYYY-MM`. No DB items stored.
`store.indexes['day:2024-01-15']` populates automatically when tasks gain the relation.

### Recurring config

Add `recur?: { unit: 'day'|'week'|'month'; interval: number }` to `BaseDoc` in `types.ts`.
Item picks it up via `Object.assign` in the constructor.

## Files

### New

| File | Purpose |
|------|---------|
| `src/domain/time-periods.ts` | Pure functions: `getPeriodID`, `generatePeriods`, `parsePeriodID`, `advancePeriod`, `todayPeriodID` |
| `src/components/ScheduleMenu.vue` | Quick-pick submenu: Today/Tomorrow/This week/Next week/This month/Custom/Remove |
| `src/components/RecurMenu.vue` | Inline form: unit select + interval input, save/clear |
| `src/views/TimeBoardView.vue` | Manages unit, anchorDate, prev/next; renders `TimeBoardColumn` per period |
| `src/components/TimeBoardColumn.vue` | Column with sticky header, tasks via `getScheduledItems(period.id)`, add-task button |

### Modified

| File | Changes |
|------|---------|
| `src/domain/types.ts` | Add `BuiltinRels.scheduledFor`, `TimePeriodID`, `RecurConfig`, `recur?` on `BaseDoc` |
| `src/domain/item.ts` | Add `recur?: RecurConfig`; add `makeTimePeriodItem(id)` — virtual Item with `childRelationKey` overridden to `scheduledFor` via `Object.defineProperty` (constructor defaults to `mainRelation` when typeDefinition is null) |
| `src/domain/relations.ts` | Add `scheduledFor` to `BuiltInRelationsConfig` |
| `src/item-controller.ts` | Add: `scheduleItem`, `unscheduleItem`, `setRecur`, `getScheduledPeriodID`, `getScheduledItems(periodID)` (wraps `store.getChildren(periodID)`), `addScheduledTask` (one-save with both `elemOf`+`scheduledFor`), private `mergeItemUpdates`. Modify `toggleDone`: if done and `item.recur` set, fetch fresh item then call `scheduleItem` with `advancePeriod` result |
| `src/components/ActionMenu.vue` | Add `scheduleMenuOpen`/`recurMenuOpen` state; "schedule" + "repeat" buttons (actionable only); render `ScheduleMenu` + `RecurMenu` as sibling panels; show current period label in button |
| `src/router/index.ts` | Add `/calendar` → `TimeBoardView` |
| `src/components/Topbar.vue` | Add calendar icon button |

## Implementation sequence

1. `types.ts` → 2. `time-periods.ts` → 3. `relations.ts` → 4. `item.ts` →
5. `item-controller.ts` → 6. `ScheduleMenu.vue` + `RecurMenu.vue` →
7. `ActionMenu.vue` → 8. `TimeBoardColumn.vue` + `TimeBoardView.vue` →
9. `router/index.ts` + `Topbar.vue` → 10. CSS

## Success criteria

- [ ] `scheduledFor` relation registered; appears in RelationMenu for tasks
- [ ] ActionMenu "schedule" button visible only for actionable items
- [ ] Quick-pick options (Today, Tomorrow, This week, Next week, This month) correctly compute period IDs
- [ ] Selecting a schedule persists `scheduledFor` relation and closes both menus
- [ ] Assigning a new schedule replaces the old one (single-parent)
- [ ] "Remove schedule" clears the relation; disabled when no schedule set
- [ ] Schedule label shown in ActionMenu "schedule" button
- [ ] `/calendar` renders columns centered on today in day view
- [ ] Tasks appear in the column matching their scheduled period
- [ ] Today's column has distinct visual highlight
- [ ] Prev/Next buttons shift the window; unit toggle switches granularity
- [ ] Adding a task from a column creates it with both `elemOf` (task toplevel) and `scheduledFor`
- [ ] `recur` config saved via RecurMenu persists on the item
- [ ] Completing a recurring task advances its schedule by the configured interval
- [ ] Completing a non-recurring task does not affect its schedule
- [ ] Undoing done on a recurring task does not create a second schedule entry

## Risks

- **`makeTimePeriodItem` routing**: `calcUpdateByRelation` reads `parent.childRelationKey` synchronously after construction; the `defineProperty` override is safe but must be verified against the actual `Item` constructor (check `src/domain/item.ts` lines 85-92 before implementing).
- **Two-write race for recurring done**: The second `scheduleItem` call fetches a fresh item from reactive storage; if the change feed hasn't processed yet, PouchDB returns a 409. Mitigation: add a `nextTick` wrapper or accept PouchDB's conflict resolution.

## Verification

1. `npm run dev` in `new-app/`
2. Schedule a task to Today via ActionMenu → confirm it appears in today's calendar column
3. Set repeat weekly; mark done → confirm schedule advances 7 days
4. Navigate prev/next on time-board → correct tasks visible
5. Add task from calendar column → appears in both list view and column
