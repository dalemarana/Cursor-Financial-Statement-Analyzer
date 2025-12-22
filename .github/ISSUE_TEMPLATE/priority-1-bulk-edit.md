---
name: "Priority 1: Bulk Edit Panel Component"
about: Build bulk operations UI for managing multiple transactions at once
title: "[Priority 1] Bulk Edit Panel Component"
labels: ["priority-1", "frontend", "feature", "phase-4"]
assignees: []
---

## Overview
Create a bulk edit panel that allows users to perform operations on multiple selected transactions simultaneously.

## Description
Users should be able to select multiple transactions and apply bulk operations like category assignment, account assignment, or deletion.

## Acceptance Criteria
- [ ] Select all / deselect all checkbox
- [ ] Bulk category assignment (with CategoryDropdown)
- [ ] Bulk account assignment (with AccountDropdown - similar to CategoryDropdown)
- [ ] Bulk delete with confirmation dialog showing count
- [ ] Progress indicator during bulk operations
- [ ] Success/error notifications after operations
- [ ] Undo functionality (optional but nice to have)
- [ ] Keyboard shortcut for select all (Cmd/Ctrl+A)
- [ ] Selected count display
- [ ] Clear selection button

## Technical Requirements
- **File:** `frontend/src/components/transactions/BulkEditPanel.tsx`
- **API:** `POST /api/transactions/bulk-update` (already implemented)
- **API:** Bulk delete endpoint (may need to implement or use loop)
- **State Management:** Share selection state with TransactionTable
- **Error Handling:** Show which transactions failed and why

## User Flow
1. User selects one or more transactions
2. Bulk edit panel appears at top/bottom of table
3. User selects action (assign category, assign account, delete)
4. If category/account: dropdown appears, user selects value
5. Confirmation dialog for delete operations
6. API call with selected transaction IDs
7. Progress indicator shows during operation
8. Success message with undo option (if applicable)
9. Table refreshes to show updated data

## Design Specs
- Sticky panel at top of table when selections are made
- Action buttons disabled when no selections
- Confirmation dialog for destructive operations
- Progress bar or circular progress for async operations

## Related Files
- `frontend/src/components/transactions/TransactionTable.tsx` - Manages selection state
- `backend/src/api/routes/transactions.py` - Bulk update endpoint

## Dependencies
- TransactionTable component (for selection state)
- CategoryDropdown component
- AccountDropdown component (create similar to CategoryDropdown)

## Estimated Effort
**3-4 days**

## Priority
**P1 - High** (Important UX feature)

---
**Related Issues:**
- TransactionTable Component
- CategoryDropdown Component

