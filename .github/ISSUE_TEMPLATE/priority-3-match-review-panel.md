---
name: "Priority 3: Match Review Panel Component"
about: Build UI for reviewing and confirming transaction matches
title: "[Priority 3] Match Review Panel Component"
labels: ["priority-3", "frontend", "feature", "phase-6"]
assignees: []
---

## Overview
Create a panel for users to review suggested transaction matches and confirm or reject them.

## Description
The matching algorithm suggests matches, but users need to review and confirm them. This panel should display suggested matches with confidence scores and allow bulk actions.

## Acceptance Criteria
- [ ] List of suggested matches with confidence scores
- [ ] Side-by-side comparison of matched transactions
- [ ] Match details display (amount difference, date difference, description similarity)
- [ ] Accept/reject buttons for individual matches
- [ ] Accept all high-confidence matches option (with threshold selector)
- [ ] Manual match search and selection
- [ ] Filter matches by confidence score
- [ ] Sort by confidence score (highest first)
- [ ] Pagination for large match lists
- [ ] Undo last action (if rejected by mistake)

## Technical Requirements
- **File:** `frontend/src/components/matching/MatchReviewPanel.tsx`
- **API:** `GET /api/matching/suggestions` (already implemented)
- **API:** `POST /api/matching/confirm/{id}` (already implemented)
- **API:** `POST /api/matching/reject/{id}` (may need to implement)

## Match Display
Each match should show:
- Transaction 1 (Paid Out) details
- Transaction 2 (Paid In) details
- Confidence score (0-100%)
- Amount match status (exact match indicator)
- Date difference (e.g., "2 days apart")
- Description similarity percentage

## User Flow
1. User navigates to match review panel
2. List of suggested matches loads
3. User reviews match details side-by-side
4. User accepts or rejects individual matches
5. OR user accepts all matches above confidence threshold
6. Confirmed matches are linked in database
7. Panel refreshes to show remaining matches

## Design Specs
- Split view for side-by-side comparison
- Color-coded confidence scores (green >80%, yellow 50-80%, red <50%)
- Accept button (green), Reject button (red)
- Checkbox for selecting multiple matches
- Bulk accept button for selected matches

## Related Files
- `frontend/src/components/matching/MatchSuggestion.tsx` - Individual match component
- `frontend/src/pages/Transactions.tsx` - May link to this panel
- Backend matching API endpoints

## Dependencies
- API endpoints for matching (already exist)
- MatchSuggestion component (separate issue)

## Estimated Effort
**3-4 days**

## Priority
**P3 - Medium** (Important but not blocking)

---
**Related Issues:**
- MatchSuggestion Component
- Unmatched Transactions View

