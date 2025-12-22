---
name: "Priority 1: Category Dropdown Component"
about: Build searchable category dropdown with grouping and creation support
title: "[Priority 1] Category Dropdown Component"
labels: ["priority-1", "frontend", "feature", "phase-4"]
assignees: []
---

## Overview
Create a searchable, grouped category dropdown component for assigning categories to transactions.

## Description
Users need an intuitive way to assign categories to transactions. The dropdown should show all available categories grouped by parent category, allow searching, and support creating new subcategories.

## Acceptance Criteria
- [ ] Searchable category list with autocomplete
- [ ] Grouped by parent category (Asset, Liability, Equity, Income, Expense)
- [ ] Collapsible groups
- [ ] Create new subcategory option (opens dialog)
- [ ] Recent categories quick select (last 5 used)
- [ ] Keyboard navigation support (arrow keys, enter, escape)
- [ ] Loading state while fetching categories
- [ ] Empty state when no categories exist
- [ ] Visual distinction between parent categories and subcategories
- [ ] Selected category highlighted

## Technical Requirements
- **File:** `frontend/src/components/transactions/CategoryDropdown.tsx`
- **API:** `GET /api/categories` (already implemented)
- **API:** `POST /api/categories` (already implemented) - for creating new subcategory
- **State Management:** Local state + React Query cache
- **Accessibility:** ARIA labels, keyboard support, focus trap

## Design Specs
- Use Material-UI Autocomplete or Select component
- Group headers styled differently from items
- Search input at top of dropdown
- "Create new..." option at bottom of dropdown
- Recent categories section at top (if applicable)

## Related Files
- `frontend/src/components/transactions/TransactionRow.tsx` - Will use this component
- `frontend/src/api/categories.ts` - API service functions (may need to create)

## Dependencies
- API endpoint: `GET /api/categories` (already exists)
- API endpoint: `POST /api/categories` (already exists)

## Estimated Effort
**2-3 days**

## Priority
**P1 - Critical** (Required for inline editing)

---
**Related Issues:**
- TransactionRow Component
- Create Category Dialog Component (optional)

