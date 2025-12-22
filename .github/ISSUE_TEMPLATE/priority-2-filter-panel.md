---
name: "Priority 2: Filter Panel Component"
about: Build comprehensive filter panel for advanced transaction filtering
title: "[Priority 2] Filter Panel Component"
labels: ["priority-2", "frontend", "feature", "phase-5"]
assignees: []
---

## Overview
Create a filter panel that allows users to apply multiple filters to transaction queries simultaneously.

## Description
The filter panel should integrate all filter types (date range, category, account, amount, etc.) into a unified, user-friendly interface.

## Acceptance Criteria
- [ ] Collapsible filter sections
- [ ] Active filter chips displayed with remove option
- [ ] Clear all filters button
- [ ] Filter count indicator (e.g., "5 filters active")
- [ ] Save filter preset button
- [ ] Load saved presets dropdown
- [ ] Reset to default button
- [ ] Filters apply automatically or with "Apply" button
- [ ] Visual feedback when filters are active
- [ ] Mobile-responsive (drawer on mobile, sidebar on desktop)

## Technical Requirements
- **File:** `frontend/src/components/filters/FilterPanel.tsx`
- **State Management:** Manage filter state, sync with URL query params
- **Integration:** Connect to TransactionTable via filter prop
- **Persistence:** Save presets to backend (API already exists)

## Filter Components to Integrate
- DateRangePicker
- CategoryFilter
- AccountFilter
- AmountRangeFilter
- TransactionTypeFilter
- MatchStatusFilter
- VendorFilter
- TextSearch

## User Flow
1. User opens filter panel
2. User applies one or more filters
3. Active filters shown as chips
4. User can remove individual filters via chip X button
5. User can save current filter combination as preset
6. User can load saved presets
7. Transactions update based on active filters

## Design Specs
- Collapsible sections with Material-UI Accordion
- Filter chips use Material-UI Chip component
- Sidebar layout on desktop, drawer on mobile
- Smooth transitions when opening/closing

## Related Files
- Individual filter components (separate issues)
- `frontend/src/hooks/useFilters.ts` - Custom hook for filter state management
- `frontend/src/pages/Transactions.tsx` - Page that will use filter panel

## Dependencies
- All individual filter components (separate issues)
- API endpoint: `GET /api/filters/presets` (may need to implement)
- API endpoint: `POST /api/filters/presets` (may need to implement)

## Estimated Effort
**2-3 days**

## Priority
**P2 - High** (Enables advanced filtering)

---
**Related Issues:**
- DateRangePicker Component
- CategoryFilter Component
- Other filter components

