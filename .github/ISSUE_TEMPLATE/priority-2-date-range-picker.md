---
name: "Priority 2: Date Range Picker Component"
about: Build date range picker for filtering transactions by date
title: "[Priority 2] Date Range Picker Component"
labels: ["priority-2", "frontend", "feature", "phase-5"]
assignees: []
---

## Overview
Create a date range picker component with preset options and custom date selection.

## Description
Users need to filter transactions by date range. The component should support both preset ranges (This Month, Last Month) and custom date selection.

## Acceptance Criteria
- [ ] Calendar picker for start and end dates
- [ ] Preset ranges: This Month, Last Month, This Year, Last Year
- [ ] Quick select buttons for preset ranges
- [ ] Relative date options ("Last 7 days", "Last 30 days", "Last 90 days")
- [ ] Custom date range selection
- [ ] Date validation (end date >= start date)
- [ ] Timezone handling (use user's timezone or UTC)
- [ ] Display selected range in readable format
- [ ] Clear/reset button
- [ ] Keyboard navigation support

## Technical Requirements
- **File:** `frontend/src/components/filters/DateRangePicker.tsx`
- **Library:** Consider react-datepicker or Material-UI DatePicker
- **Format:** ISO 8601 dates for API calls
- **State:** Controlled component with value and onChange props

## Design Specs
- Material-UI DatePicker or similar
- Preset buttons arranged horizontally or vertically
- Selected dates highlighted
- Disable future dates (optional, depending on requirements)
- Date format: MM/DD/YYYY or DD/MM/YYYY (locale-based)

## User Flow
1. User clicks date range input
2. Calendar opens
3. User selects start date
4. User selects end date
5. OR user clicks preset button (applies immediately)
6. Dates validate automatically
7. Range applied to filter

## Related Files
- `frontend/src/components/filters/FilterPanel.tsx` - Parent component
- `frontend/src/hooks/useFilters.ts` - Filter state management

## Dependencies
- Material-UI DatePicker or react-datepicker library

## Estimated Effort
**1-2 days**

## Priority
**P2 - High** (Essential filter feature)

---
**Related Issues:**
- FilterPanel Component

