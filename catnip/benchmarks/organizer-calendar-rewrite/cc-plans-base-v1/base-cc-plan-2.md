# Calendar & Time-Based Planning: Implementation Plan

## Context

**Old app**: Vue 2 + JavaScript + Vue Material + Moment.js. Calendar features are fully implemented.  
**New app**: Vue 3 + TypeScript + Vite. Architecture is in place; calendar features are entirely missing.

The goal is to reimplement the calendar and time-based planning features in the new app, using the new architecture properly rather than porting code mechanically. Data format compatibility with the old app is not required.

---

## What the Old App Does (Feature Inventory)

### Core concept: `plannedFor`
Every item can be "planned for" a time bucket — a **day**, **week**, **month**, or a custom **list** (backlog). This is a first-class ordered relation: items are sorted within each bucket, can be dragged between buckets, and their position is preserved.

### Time Board view
A multi-column layout with three parallel hierarchies:
- **Days** — one column per day, past and future, with "show more" navigation
- **Weeks** — one column per ISO week
- **Months** — one column per calendar month
- **Backlog** — unscheduled items (shared team backlog)
- **Custom lists** — user-created lists can appear as additional columns

Each column is a section showing items planned for that time unit. Users can hide/show any hierarchy (e.g. show only weeks). Layout preference is persisted in the database.

### Scheduling UI
- **Date menu on task cards** — quick options: Today, Tomorrow, This week, Next week, This month, Backlog, Remove, Custom date
- **Date dialog** — modal for bulk-scheduling selected items; options include "in N weeks", "in N months", custom picker
- **Date chip on cards** — shows where the item is planned (e.g. "Today", "Next week", "Jan 2025")

### Recurring tasks
Items can have a `repeat` configuration (`unit: day|week|month`, `increment: number`). When a recurring task is marked done, a new copy is created with the date advanced by the repeat interval.

### Google Calendar integration
Two-way sync with Google Calendar. Events from Google Calendar appear as items in the time board. Items can be exported as Google Calendar events. Event items carry `gcal_id`, `gcal_link`, and a full `event` object with start/end times.

---

## New App Architecture (Relevant Patterns)

### Relation system
Relations are the core abstraction. Each relation is registered in `RelationRegistry` and has three layers:
1. **RelationController** (`Relation` class, `src/domain/relations.ts`) — calculates placements, validates constraints, handles single- vs multi-parent semantics
2. **RelationDriver** (`ParentPointerRelation`, `src/implementation/relation-driver.ts`) — pure math for mudder-based sequence values
3. **ItemController** (`src/item-controller.ts`) — top-level orchestrator; groups, persists, delegates

### Built-in types and relations
Defined in `src/domain/types.ts`:
```
BuiltinTypes: root, itemType, list, label, task, note
BuiltinRels: mainRelation ("builtin.elemOf"), labels ("builtin.labels")
```

### Item data structure
```typescript
type BaseDoc = {
  _id: string;
  text: string;
  type: ItemType;
  trashed?: boolean;
  relations?: ItemRelations;  // keyed by relation key
}
// Relations stored as: Record<RelationKey, Record<parentId, { seq?: string }>>
```

---

## Implementation Plan

### Phase 1 — Data Model & Domain Layer

#### 1.1 Add `plannedFor` relation

Register a new built-in relation `"builtin.plannedFor"` (add to `BuiltinRels` in `types.ts`).

Characteristics:
- **Ordered** (items have a `seq` field within their bucket)
- **Single-parent** (each item is planned for at most one time bucket at a time)
- **Parent types**: virtual time-bucket nodes (day/week/month) and list items

The relation should be registered in `RelationRegistry` in `main.ts`, using the existing `Relation` class. No new relation infrastructure is needed — this fits the existing model.

#### 1.2 Add time-bucket virtual nodes

Time buckets (days, weeks, months) do not need to be stored as database documents. They are virtual: their IDs are deterministic strings derived from the date.

Define a module `src/domain/time-buckets.ts` with:
- Bucket ID generation: `day:2025-05-07`, `week:2025-W19`, `month:2025-05`
- Bucket parsing: extract unit and key from ID
- Navigation helpers: next/previous bucket, current bucket for a date
- Display formatting: "Today", "Tomorrow", "Yesterday", "This week", "Next week", relative month/week labels, absolute fallback

Use the native `Intl` API and `Date` — no moment.js. The old app's `time-utils.js` is the reference for what formatting is needed.

#### 1.3 Extend Item type

Add optional fields to `Item` (in `src/domain/item.ts`):

```typescript
repeat?: {
  unit: 'day' | 'week' | 'month';
  increment: number;
}

// Google Calendar fields (Phase 3 only, can be deferred)
gcalId?: string;
gcalLink?: string;
gcalEvent?: { ... };
```

The `plannedFor` relation itself is stored in `item.relations` using the standard relation mechanism — no special field needed.

#### 1.4 Recurring task logic

Add a method to `ItemController` (or a helper module): when an item with `repeat` is marked done, create a new item with the same content, same `repeat` config, and `plannedFor` advanced by the repeat interval. The new item is unfinished.

This should be triggered from the existing "mark done" flow in `ItemController`.

---

### Phase 2 — Calendar View (UI)

#### 2.1 Router: add `/calendar` route

Add a new route `/calendar` → `CalendarView.vue` in `src/router/index.ts`.

#### 2.2 `CalendarView.vue` — top-level shell

Manages:
- Which hierarchies are visible (days / weeks / months / backlog / lists)
- How many past and future sections to show per hierarchy
- Layout persistence (save/load from a special item in the database, e.g. `_id: "meta.calendar-layout"`)

Renders a horizontal multi-column layout. Each visible hierarchy contributes a group of columns.

#### 2.3 `TimeBucketColumn.vue` — a single time bucket column

Props: `bucketId` (e.g. `"week:2025-W19"`), `label` (formatted display name), `past | current | future` class.

Internally:
- Loads all items planned for this bucket via `ItemController`, ordered by `seq`
- Renders using existing `ItemList.vue` / `ElementList.vue` components
- Accepts drag-and-drop to reorder items or move items from another bucket

The column header shows the formatted label (with relative names for current/adjacent periods).

#### 2.4 `DateChip.vue` — inline display of plannedFor on a card

A small chip on `ItemCard.vue` showing where the item is planned. Uses the same relative formatting as column headers. Clicking it opens the date menu.

Add this chip to the existing `ItemCard.vue` rendering when the item has a `plannedFor` relation.

#### 2.5 `DateMenu.vue` — quick scheduling dropdown

A dropdown (extends `BaseMenu.vue`) with options:
- Today / Tomorrow / This week / Next week / This month
- Backlog (clears date assignment, moves to backlog list)
- Remove (unplans the item entirely)
- Custom date (opens a native `<input type="date">` or a date picker component)

Each option calls `ItemController` to update the `plannedFor` relation.

#### 2.6 `DateDialog.vue` — bulk scheduling modal

Used when multiple items are selected. Options:
- In N weeks (2, 3)
- In N months (1, 2)
- Custom date picker

Applies to all selected items.

#### 2.7 `CalendarSettings.vue` — visibility toggles

Panel (or modal) for:
- Toggling each hierarchy (days / weeks / months / backlog) on/off
- Selecting custom lists to show as columns

Persists to the `meta.calendar-layout` document.

---

### Phase 3 — Google Calendar Integration (Optional / Later)

This is a significant feature that can be deferred. Implement only after Phase 1 and 2 are solid.

#### 3.1 `gcalendar.ts` — API wrapper

Port `gcalendar-utils.js` logic to TypeScript:
- OAuth2 flow (client-side, same as old app)
- `loadEvents()` — fetch events from Google Calendar and upsert them as items with `type: "event"` and `gcalId`
- `exportToCalendar()` — push items to Google Calendar
- `updateEvent()` — sync changes back (with etag conflict detection)

#### 3.2 Event item type

Register `"builtin.event"` in `TypeRegistry`. Events differ from tasks in:
- They have a start time and duration (`dur` in minutes), or a full-day flag
- They are created/updated by the GCal sync and are read-only in most UIs
- They show a time chip on the card

#### 3.3 Sync UI

A settings panel to:
- Authenticate with Google
- Select which calendars to sync
- Trigger manual sync / show last sync time

---

## Implementation Order

1. `src/domain/time-buckets.ts` — date utilities, bucket ID helpers, formatting
2. `src/domain/types.ts` — add `plannedFor` to `BuiltinRels`, add `repeat` to Item
3. `src/domain/item.ts` — add repeat field, update `plannedFor` relation handling
4. `src/item-controller.ts` — register `plannedFor` relation, add recurring-task logic on done
5. `src/router/index.ts` — add `/calendar` route
6. `src/components/DateChip.vue` — planned-for chip
7. `src/components/DateMenu.vue` — scheduling dropdown
8. `src/components/TimeBucketColumn.vue` — single bucket column
9. `src/views/CalendarView.vue` — top-level calendar shell
10. `src/components/DateDialog.vue` — bulk scheduling modal
11. `src/components/CalendarSettings.vue` — visibility/layout settings
12. Wire `DateChip` and `DateMenu` into `ItemCard.vue`

Phase 3 (GCal) can start independently after step 4.

---

## Key Design Decisions

**Virtual time buckets**: Days/weeks/months are not stored in the database; their IDs are computed strings. The `plannedFor` relation stores a parent key that may reference a non-existent document — `ItemController` must handle this gracefully (no error if bucket document is missing).

**No moment.js**: Use the native `Intl.DateTimeFormat` and `Date` APIs. The formatting requirements (relative names, week numbers) are modest enough that a moment.js dependency is unnecessary.

**Reuse existing components**: `ItemList`, `ElementList`, `ItemCard`, `ActionMenu`, `BaseMenu` are already built and work. The calendar view should compose these rather than reimplementing item rendering.

**Layout persistence**: Store layout preference as a special document in PouchDB with a fixed `_id` (`meta.calendar-layout`). This matches how the old app stored the `calendar-view-layout` document, but using the new app's storage abstraction.

**`plannedFor` is a standard relation**: It uses the same `Relation` class, `RelationDriver`, and `ItemController` machinery as `mainRelation`. No special-casing in the storage layer is needed.
