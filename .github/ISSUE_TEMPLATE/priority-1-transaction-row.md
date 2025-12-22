---
name: "Priority 1: Transaction Row Component"
about: Build individual transaction row component with formatting and actions
title: "[Priority 1] Transaction Row Component"
labels: ["priority-1", "frontend", "feature", "phase-4"]
assignees: []
---

## Overview
Create a reusable TransactionRow component to display individual transactions with proper formatting, status indicators, and quick actions.

## Description
Each transaction row should display formatted data, show match status, and provide quick actions for editing, deleting, or viewing details.

## Acceptance Criteria
- [ ] Date formatting with relative dates ("2 days ago", "Last week")
- [ ] Amount formatting with color coding (green for income, red for expenses)
- [ ] Category badge with color coding
- [ ] Match status indicator (matched/unmatched/pending) with visual indicator
- [ ] Quick actions menu (edit, delete, view details, match)
- [ ] Hover effects and interaction feedback
- [ ] Inline editing support (for category and account)
- [ ] Loading state during updates
- [ ] Confirmation dialog for delete action
- [ ] Click handler to view transaction details

## Technical Requirements
- **File:** `frontend/src/components/transactions/TransactionRow.tsx`
- **Props:** Transaction data, onEdit, onDelete, onMatch callbacks
- **Styling:** Material-UI components, consistent with design system
- **Accessibility:** Keyboard navigation, focus management

## Design Specs
- **Amount colors:** 
  - Green (#4caf50) for positive amounts (Paid In)
  - Red (#f44336) for negative amounts (Paid Out)
- **Match status colors:**
  - Green badge for matched
  - Orange badge for pending review
  - Gray badge for unmatched

## Related Files
- `frontend/src/components/transactions/TransactionTable.tsx` - Parent component
- `frontend/src/models/Transaction.ts` - TypeScript interface (may need to create)

## Dependencies
- CategoryDropdown component (for inline editing)
- API endpoints: `PUT /api/transactions/{id}`, `DELETE /api/transactions/{id}` (already exist)

## Estimated Effort
**2-3 days**

## Priority
**P1 - Critical** (Required for TransactionTable)

---
**Related Issues:**
- TransactionTable Component
- CategoryDropdown Component

