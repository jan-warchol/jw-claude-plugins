# Time-Based Planning Reimplementation Plan

## Overview

The old app has a "time board" feature: items can be assigned to a day, week, or month (or left in a backlog), displayed in a columnar calendar view, and optionally configured to repeat. The new app has a clean domain-driven architecture with a generic relation system. This plan describes how to reimplement time-based planning in the new app, taking advantage of that architecture rather than cargo-culting the old one.

---

## What Exists in the Old App

### Core Data Model

Items carry a `plannedFor` field:

```js
plannedFor: {
  parentClass: 'day' | 'week' | 'month' | 'list',
  parentKey: string,  // ISO date (YYYY-MM-DD) or list ID
  seq: string         // mudder sequence for ordering within the slot
}
```

Repeating items carry a `repeat` field:

```js
repeat: {
  increment: number,
  unit: 'day' | 'week' | 'month' | 'year',
  repeated: boolean  // true once next occurrence has been generated
}
```

### Features

1. **Time Board view** — columns: Days (today, ±N days), Weeks (this week, ±N), Months (this month, ±N), Backlog (unplanned), optional custom list columns.
2. **Quick-schedule dialog** — buttons like "in 2 weeks", "next month", plus a date picker.
3. **Repeating tasks** — on completion, if `repeat` is set, a new occurrence is created at the next calculated date and the original is marked `repeated: true`.
4. **Relative time labels** — "Yesterday", "This week", "Last month", etc.
5. **Google Calendar sync** — bi-directional import/export for items planned on a specific day.

---

## What Exists in the New App

The new app has:

- A **generic relation system** (`relations.ts`, `relation-registry.ts`) supporting ordered/unordered, single/multi-parent relations.
- An **item type registry** (`type-registry.ts`) for extensible types.
- An **`ItemController`** (`item-controller.ts`) that orchestrates persistence and relation logic.
- A reactive PouchDB-backed store.
- Existing built-in types: `builtin.list`, `builtin.task`, `builtin.note`, `builtin.label`.
- Existing built-in relations: `builtin.elemOf` (primary hierarchy), `builtin.labels`.

There is **no** time-based relation, no calendar view, and no repeat logic yet.

---

## Architecture Decision: Virtual Time Containers

Rather than storing raw date strings in a custom field (as old-app does), the new app should model time slots as **first-class items**:

- Each calendar slot (a specific day, week, or month) is an item of type `builtin.day` / `builtin.week` / `builtin.month`.
- Items are planned by making them children of a slot item via a new `builtin.plannedFor` relation.
- Slot items are auto-created on demand (when the view initialises or when an item is first scheduled into a slot that doesn't exist yet).
- The Backlog is a single persistent `builtin.backlog` item (created once, like the root).

This fits naturally into the existing architecture: the ItemController already handles ordered child relations, and the reactive cache already computes `getChildren(slotItem)`.

---

## Phase 1: Domain / Data Layer

### 1.1 New Item Types

Add to `type-registry.ts` (or a new `time-types.ts` file registered at startup):

| Type key | Purpose |
|---|---|
| `builtin.day` | Represents a calendar day. `_id` encodes the ISO date, e.g. `day.2026-05-08`. |
| `builtin.week` | Represents an ISO week. `_id` encodes year+week, e.g. `week.2026-W19`. |
| `builtin.month` | Represents a calendar month. `_id` encodes year+month, e.g. `month.2026-05`. |
| `builtin.backlog` | Single "unplanned" bucket. `_id` = `builtin.backlog`. |
| `builtin.timeboard` | Virtual root for the calendar view (not shown in normal hierarchy). |

Slot items should be `readOnly: true` so they cannot be edited or deleted through normal UI flows.

### 1.2 New Relation

Add `builtin.plannedFor` to `relation-registry.ts`:

```typescript
{
  key: 'builtin.plannedFor',
  ordered: true,
  multiParent: false,   // an item is planned in exactly one slot at a time
  required: false       // items without plannedFor are simply unplanned
}
```

This mirrors how `builtin.elemOf` works but is independent of the primary hierarchy. An item can simultaneously be a child of a list (`elemOf`) and planned for a day (`plannedFor`).

### 1.3 Repeat Metadata

Store repeat config directly on the item as a typed property (not inside `relations`):

```typescript
interface RepeatConfig {
  increment: number;
  unit: 'day' | 'week' | 'month' | 'year';
}

// On the item:
repeat?: RepeatConfig;
repeated?: boolean;
```

Add these fields to the Item interface in `item.ts`.

---

## Phase 2: Time Utilities

Create `/src/time-utils.ts` (adapted from the old app's `time-utils.js`, but in TypeScript with the `temporal` Temporal API or `date-fns` instead of `moment.js`):

```typescript
// Key functions to implement:
todayISO(): string
thisWeekISO(): string   // Monday of current ISO week
thisMonthISO(): string

dayID(iso: string): string          // "day.2026-05-08"
weekID(iso: string): string         // "week.2026-W19"
monthID(iso: string): string        // "month.2026-05"

formatDayLabel(iso: string): string   // "Today", "Yesterday", "Monday", "8 May"
formatWeekLabel(iso: string): string  // "This week", "Last week", "19 May – 25 May"
formatMonthLabel(iso: string): string // "May", "April 2025"

calcRepeatDate(plannedISO: string, repeat: RepeatConfig): string
// Returns the ISO date/week/month for the next occurrence

slotGranularity(slotType: 'day'|'week'|'month'): number  // days
```

Use `date-fns` (already likely compatible with the Vite stack and tree-shakeable). Avoid `moment.js`.

---

## Phase 3: Slot Item Management

Create `/src/time-slots.ts` — a composable or utility that ensures slot items exist in the DB:

```typescript
async function ensureSlotItem(
  controller: ItemController,
  slotID: string,
  slotType: 'day' | 'week' | 'month'
): Promise<Item>
```

- Checks reactive cache first (cheap path).
- If missing, creates the slot item with `readOnly: true` and parents it under `builtin.timeboard` via `builtin.elemOf`.
- Called lazily: when the time board initialises, and when an item is scheduled into a new slot.

Also add a helper to `ItemController` (or to `time-slots.ts`):

```typescript
async planItem(item: Item, slotID: string): Promise<void>
async unplanItem(item: Item): Promise<void>
async replanItem(item: Item, newSlotID: string): Promise<void>
async bulkReplan(items: Item[], newSlotID: string): Promise<void>
```

These wrap `replaceParents` / `removeParents` on the `builtin.plannedFor` relation.

---

## Phase 4: Repeat Logic

Add repeat handling to `ItemController.toggleDone`:

```typescript
async toggleDone(item: Item): Promise<void> {
  // existing: set/clear doneAt

  if (item.doneAt && item.repeat && !item.repeated) {
    const currentSlot = plannedForRelation.getParent(item);
    if (currentSlot) {
      const nextISO = calcRepeatDate(slotISO(currentSlot), item.repeat);
      const nextSlotID = slotIDFromISO(nextISO, granularityOf(currentSlot));
      await ensureSlotItem(controller, nextSlotID, granularityOf(currentSlot));
      await duplicateItemIntoSlot(item, nextSlotID);
    }
    await update(item, { repeated: true });
  }
}
```

`duplicateItemIntoSlot`: creates a new item copying `text`, `type`, `repeat`, `relations.elemOf` (same list parent), and sets `plannedFor` to the new slot. Does **not** copy `doneAt`, `repeated`, or `_id`.

---

## Phase 5: Time Board View

### 5.1 Component Structure

```
TimeBoardView.vue
├── TimeBoardColumn.vue  (reusable for day/week/month/backlog)
│   ├── SlotSection.vue  (one calendar slot: header + item list)
│   │   ├── [item header/label]
│   │   └── ItemCard.vue  (existing component, reused)
│   └── AddItem.vue       (existing component, reused)
└── TimeBoardSettings.vue
```

### 5.2 TimeBoardView

- Rendered at route `/plan` (add to router).
- Computes which slot IDs are in range (e.g. today ± days, this week ± weeks, this month ± months).
- Calls `ensureSlotItem` for all visible slots on mount and when range changes.
- Reads children of each slot via `controller.getChildren(slotItem)` filtered by `builtin.plannedFor`.
- Backlog: items where `plannedForRelation.getParent(item) === null`.

Default ranges (configurable in settings):

| Column | Past | Future |
|---|---|---|
| Days | 0 | 2 |
| Weeks | 0 | 1 |
| Months | 0 | 1 |

### 5.3 SlotSection

- Header shows human-readable label (`formatDayLabel`, etc.) + absolute date.
- Past slots collapsed by default (expandable).
- Items draggable between slots (use existing or add vue-draggable).
- "Move to…" quick action on each item card.

### 5.4 Settings

Persist as a single `builtin.timeboard-settings` document (not an item — a settings doc):

```typescript
interface TimeBoardSettings {
  columns: Array<'days' | 'weeks' | 'months' | 'backlog'>;
  past: { days: number; weeks: number; months: number };
  future: { days: number; weeks: number; months: number };
}
```

Stored in PouchDB directly (not through ItemController) with a fixed `_id`.

---

## Phase 6: Schedule Dialog

Create `ScheduleDialog.vue` — accessible from the item action menu (`ActionMenu.vue`):

- Quick-pick buttons: Today, Tomorrow, This week, Next week, This month, Next month, In 2 weeks, In 2 months.
- Date picker for specific day (opens browser native `<input type="date">` or a lightweight calendar picker).
- "Remove from plan" (unplan) option.
- On selection: calls `planItem(item, slotID)` and ensures the slot item exists.

Also add a minimal inline date chip to `ItemCard.vue` (shown when item is planned) that opens the dialog on click — equivalent to the old app's `selected-date-menu`.

---

## Phase 7: Navigation

Add the time board as a top-level navigation entry:

- New route: `/plan` → `TimeBoardView`.
- Add link in `Topbar.vue`.
- Keep existing `/` and `/view/:itemID` routes unchanged.

---

## Out of Scope (for this iteration)

- **Google Calendar integration** — significant additional complexity; can be added later as the slot item architecture maps cleanly onto GCal events.
- **Drag-and-drop reordering** within a slot — the mudder-based ordering already works; a drag library can be added once the base view is stable.
- **Mobile layout** — the columnar view can be simplified to a single-column scroll on small screens as a follow-up.

---

## File Checklist

| File | Action |
|---|---|
| `src/time-utils.ts` | Create |
| `src/time-slots.ts` | Create |
| `src/domain/item.ts` | Add `repeat`, `repeated` fields |
| `src/domain/relation-registry.ts` | Register `builtin.plannedFor` |
| `src/domain/type-registry.ts` | Register `builtin.day`, `week`, `month`, `backlog`, `timeboard` |
| `src/item-controller.ts` | Extend `toggleDone` with repeat logic; add plan/unplan helpers |
| `src/router.ts` | Add `/plan` route |
| `src/views/TimeBoardView.vue` | Create |
| `src/components/TimeBoardColumn.vue` | Create |
| `src/components/SlotSection.vue` | Create |
| `src/components/ScheduleDialog.vue` | Create |
| `src/components/ActionMenu.vue` | Add "Schedule" action |
| `src/components/ItemCard.vue` | Add planned-for date chip |
| `src/components/Topbar.vue` | Add Plan nav link |

---

## Implementation Order

1. **Time utilities** (`time-utils.ts`) — pure functions, no dependencies, easy to test.
2. **Domain layer** — add types, relation, and item fields.
3. **Slot management** (`time-slots.ts`) + plan/unplan helpers in ItemController.
4. **Time Board view** (basic, no drag/drop) — verify scheduling works end to end.
5. **Schedule dialog** — wire into ActionMenu and ItemCard.
6. **Repeat logic** — extend toggleDone.
7. **Settings** — persist and restore column/range preferences.
