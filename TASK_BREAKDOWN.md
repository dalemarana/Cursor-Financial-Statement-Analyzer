# Detailed Task Breakdown - Financial Statement Analyzer

This document provides granular task breakdowns for each development phase. Each task is sized for 1-3 days of work and includes acceptance criteria and dependencies.

---

## Phase 4: Frontend Transaction Management (Priority 1)

### Task 4.1: Transaction Table Component - Core Structure
**Estimated Effort:** 1 day  
**Dependencies:** None  
**File:** `frontend/src/components/transactions/TransactionTable.tsx`

**Subtasks:**
- [ ] Create component file with TypeScript interface
- [ ] Set up Material-UI Table component structure
- [ ] Define table columns (date, description, amount, category, account, match status)
- [ ] Implement basic data fetching with React Query
- [ ] Add loading state (skeleton loaders)
- [ ] Add error handling and error display
- [ ] Add empty state component
- [ ] Style table with Material-UI theme

**Acceptance Criteria:**
- Table displays transactions from API
- Shows loading skeleton while fetching
- Displays error message on API failure
- Shows empty state when no transactions

---

### Task 4.2: Transaction Table - Sorting & Pagination
**Estimated Effort:** 1 day  
**Dependencies:** Task 4.1  
**File:** `frontend/src/components/transactions/TransactionTable.tsx`

**Subtasks:**
- [ ] Implement column sorting (ascending/descending)
- [ ] Add sort indicators (arrows) to column headers
- [ ] Implement pagination component
- [ ] Add page size selector (10, 25, 50, 100)
- [ ] Sync pagination state with URL query params
- [ ] Update API call with sort and pagination params

**Acceptance Criteria:**
- All columns are sortable
- Sort state persists in URL
- Pagination controls work correctly
- Page size changes update display
- API receives correct sort/pagination params

---

### Task 4.3: Transaction Table - Row Selection
**Estimated Effort:** 0.5 days  
**Dependencies:** Task 4.1  
**File:** `frontend/src/components/transactions/TransactionTable.tsx`

**Subtasks:**
- [ ] Add checkbox column for selection
- [ ] Implement single row selection
- [ ] Implement multiple row selection
- [ ] Add "select all" checkbox in header
- [ ] Track selected rows in state
- [ ] Pass selected rows to parent component

**Acceptance Criteria:**
- Users can select single or multiple rows
- Select all/deselect all works
- Selected count displays correctly
- Selected rows highlighted visually

---

### Task 4.4: Transaction Row Component
**Estimated Effort:** 1 day  
**Dependencies:** Task 4.1  
**File:** `frontend/src/components/transactions/TransactionRow.tsx`

**Subtasks:**
- [ ] Create component with transaction props
- [ ] Format date with relative dates library (date-fns)
- [ ] Format amount with currency symbol and color coding
- [ ] Create category badge component
- [ ] Add match status indicator with colors
- [ ] Implement hover effects
- [ ] Add click handler for row selection
- [ ] Style with Material-UI

**Acceptance Criteria:**
- Dates show relative format ("2 days ago")
- Amounts colored correctly (green/red)
- Category badges display with colors
- Match status clearly visible
- Row hover effect works
- Click selects row

---

### Task 4.5: Transaction Row - Quick Actions Menu
**Estimated Effort:** 0.5 days  
**Dependencies:** Task 4.4  
**File:** `frontend/src/components/transactions/TransactionRow.tsx`

**Subtasks:**
- [ ] Add three-dot menu button to row
- [ ] Create dropdown menu component
- [ ] Add menu items: Edit, Delete, View Details, Match
- [ ] Implement click handlers for each action
- [ ] Add confirmation dialog for delete
- [ ] Style menu with Material-UI Menu component

**Acceptance Criteria:**
- Menu appears on three-dot click
- All actions available in menu
- Delete requires confirmation
- Menu closes after action

---

### Task 4.6: Category Dropdown Component - Core
**Estimated Effort:** 1 day  
**Dependencies:** None  
**File:** `frontend/src/components/transactions/CategoryDropdown.tsx`

**Subtasks:**
- [ ] Create component with controlled value prop
- [ ] Set up Material-UI Autocomplete component
- [ ] Fetch categories from API using React Query
- [ ] Display categories in dropdown
- [ ] Implement search/filter functionality
- [ ] Handle selection and onChange
- [ ] Add loading state

**Acceptance Criteria:**
- Dropdown displays all categories
- Search filters categories
- Selection updates value
- Loading state shown while fetching

---

### Task 4.7: Category Dropdown - Grouping & Creation
**Estimated Effort:** 1 day  
**Dependencies:** Task 4.6  
**File:** `frontend/src/components/transactions/CategoryDropdown.tsx`

**Subtasks:**
- [ ] Group categories by parent category
- [ ] Display groups with headers
- [ ] Make groups collapsible
- [ ] Add "Create new subcategory" option
- [ ] Create dialog for new subcategory form
- [ ] Implement API call to create category
- [ ] Update dropdown after creation
- [ ] Add recent categories section

**Acceptance Criteria:**
- Categories grouped by parent
- Groups can be expanded/collapsed
- New subcategory can be created
- Dropdown updates after creation
- Recent categories shown at top

---

### Task 4.8: Inline Editing for Category
**Estimated Effort:** 1 day  
**Dependencies:** Task 4.4, Task 4.7  
**File:** `frontend/src/components/transactions/TransactionRow.tsx`

**Subtasks:**
- [ ] Make category cell editable on click
- [ ] Replace text with CategoryDropdown on edit
- [ ] Save changes on selection
- [ ] Update transaction via API
- [ ] Show loading state during update
- [ ] Handle update errors
- [ ] Optimistic UI update
- [ ] Cancel editing on escape key

**Acceptance Criteria:**
- Category editable by clicking cell
- Dropdown appears in cell
- Changes save to API
- Loading indicator during save
- Errors handled gracefully
- Can cancel edit

---

### Task 4.9: Inline Editing for Account
**Estimated Effort:** 0.5 days  
**Dependencies:** Task 4.8 (similar pattern)  
**File:** `frontend/src/components/transactions/TransactionRow.tsx`

**Subtasks:**
- [ ] Create AccountDropdown component (similar to CategoryDropdown)
- [ ] Make account cell editable
- [ ] Implement save functionality
- [ ] Handle API updates

**Acceptance Criteria:**
- Account editable like category
- Changes save correctly

---

### Task 4.10: Bulk Edit Panel - Selection State
**Estimated Effort:** 0.5 days  
**Dependencies:** Task 4.3  
**File:** `frontend/src/components/transactions/BulkEditPanel.tsx`

**Subtasks:**
- [ ] Create component file
- [ ] Accept selected transactions as prop
- [ ] Show panel only when transactions selected
- [ ] Display selected count
- [ ] Add "Clear Selection" button
- [ ] Style panel as sticky bar

**Acceptance Criteria:**
- Panel appears when selections made
- Shows correct count
- Clears selections on button click

---

### Task 4.11: Bulk Edit Panel - Bulk Category Assignment
**Estimated Effort:** 1 day  
**Dependencies:** Task 4.10, Task 4.7  
**File:** `frontend/src/components/transactions/BulkEditPanel.tsx`

**Subtasks:**
- [ ] Add bulk category assignment button
- [ ] Show CategoryDropdown when clicked
- [ ] Collect selected transaction IDs
- [ ] Call bulk-update API endpoint
- [ ] Show progress indicator
- [ ] Handle success/error states
- [ ] Refresh transaction list
- [ ] Show success notification

**Acceptance Criteria:**
- Bulk category assignment works
- API called with all selected IDs
- Progress shown during operation
- Success/error notifications displayed

---

### Task 4.12: Bulk Edit Panel - Bulk Delete
**Estimated Effort:** 0.5 days  
**Dependencies:** Task 4.10  
**File:** `frontend/src/components/transactions/BulkEditPanel.tsx`

**Subtasks:**
- [ ] Add bulk delete button
- [ ] Create confirmation dialog with count
- [ ] Implement delete API calls (loop or batch)
- [ ] Show progress indicator
- [ ] Handle errors
- [ ] Refresh list after deletion

**Acceptance Criteria:**
- Confirmation required for delete
- All selected transactions deleted
- Errors handled per transaction
- List refreshes after deletion

---

### Task 4.13: Complete Transactions Page
**Estimated Effort:** 1 day  
**Dependencies:** All above tasks  
**File:** `frontend/src/pages/Transactions.tsx`

**Subtasks:**
- [ ] Integrate TransactionTable component
- [ ] Add page header with title
- [ ] Add search bar (placeholder for now)
- [ ] Add export button (placeholder)
- [ ] Add filter toggle button
- [ ] Set up layout with sidebar/drawer
- [ ] Handle responsive design
- [ ] Add transaction detail modal (optional)

**Acceptance Criteria:**
- Page displays transaction table
- All components integrated
- Layout is responsive
- Navigation works

---

## Phase 5: Filtering & Search UI (Priority 2)

### Task 5.1: Filter Panel - Core Structure
**Estimated Effort:** 0.5 days  
**Dependencies:** None  
**File:** `frontend/src/components/filters/FilterPanel.tsx`

**Subtasks:**
- [ ] Create component file
- [ ] Set up collapsible sections with Accordion
- [ ] Create filter state management (useFilters hook)
- [ ] Add clear all filters button
- [ ] Add filter count indicator
- [ ] Style as sidebar/drawer

**Acceptance Criteria:**
- Panel structure in place
- State management works
- Clear all button functions
- Count displays correctly

---

### Task 5.2: Date Range Picker Component
**Estimated Effort:** 1 day  
**Dependencies:** None  
**File:** `frontend/src/components/filters/DateRangePicker.tsx`

**Subtasks:**
- [ ] Install date picker library (react-datepicker or MUI)
- [ ] Create component with start/end date inputs
- [ ] Add preset buttons (This Month, Last Month, etc.)
- [ ] Implement date validation
- [ ] Format dates for API calls
- [ ] Handle timezone
- [ ] Style component

**Acceptance Criteria:**
- Date range selectable
- Presets work correctly
- Dates validate properly
- Format matches API requirements

---

### Task 5.3: Category Filter Component
**Estimated Effort:** 1 day  
**Dependencies:** None  
**File:** `frontend/src/components/filters/CategoryFilter.tsx`

**Subtasks:**
- [ ] Create multi-select dropdown
- [ ] Group categories by parent
- [ ] Add tree view for subcategories
- [ ] Implement select all/none per group
- [ ] Add search within categories
- [ ] Add "Uncategorized" option
- [ ] Style component

**Acceptance Criteria:**
- Multi-select works
- Grouping displays correctly
- Select all/none functions
- Search filters options

---

### Task 5.4: Account Filter Component
**Estimated Effort:** 0.5 days  
**Dependencies:** Task 5.3 (similar pattern)  
**File:** `frontend/src/components/filters/AccountFilter.tsx`

**Subtasks:**
- [ ] Create multi-select component
- [ ] Fetch accounts from API
- [ ] Display accounts in dropdown
- [ ] Handle selection

**Acceptance Criteria:**
- Accounts filterable
- Multi-select works

---

### Task 5.5: Amount Range Filter Component
**Estimated Effort:** 0.5 days  
**Dependencies:** None  
**File:** `frontend/src/components/filters/AmountRangeFilter.tsx`

**Subtasks:**
- [ ] Create min/max input fields
- [ ] Add range slider component
- [ ] Sync slider with inputs
- [ ] Format as currency
- [ ] Validate range (min < max)

**Acceptance Criteria:**
- Amount range selectable
- Slider syncs with inputs
- Validation works

---

### Task 5.6: Other Filter Components
**Estimated Effort:** 1 day (all together)  
**Dependencies:** None  
**Files:** Multiple filter component files

**Subtasks:**
- [ ] TransactionTypeFilter (toggle buttons)
- [ ] MatchStatusFilter (toggle buttons)
- [ ] VendorFilter (autocomplete)
- [ ] TextSearch (input field)

**Acceptance Criteria:**
- All filters functional
- Styled consistently

---

### Task 5.7: Active Filter Chips
**Estimated Effort:** 0.5 days  
**Dependencies:** Task 5.1  
**File:** `frontend/src/components/filters/FilterPanel.tsx`

**Subtasks:**
- [ ] Display active filters as chips
- [ ] Add remove button (X) to each chip
- [ ] Update filter state on chip remove
- [ ] Style chips with Material-UI

**Acceptance Criteria:**
- Active filters shown as chips
- Can remove individual filters
- State updates correctly

---

### Task 5.8: Filter Presets
**Estimated Effort:** 1 day  
**Dependencies:** Task 5.1  
**File:** `frontend/src/components/filters/FilterPresets.tsx`

**Subtasks:**
- [ ] Create save preset dialog
- [ ] Implement API call to save preset
- [ ] Create load presets dropdown
- [ ] Add delete preset option
- [ ] Add default presets
- [ ] Integrate with FilterPanel

**Acceptance Criteria:**
- Can save current filters
- Can load saved presets
- Can delete presets
- Default presets available

---

### Task 5.9: Filter Integration with Transactions Page
**Estimated Effort:** 0.5 days  
**Dependencies:** All filter components  
**File:** `frontend/src/pages/Transactions.tsx`

**Subtasks:**
- [ ] Connect FilterPanel to Transactions page
- [ ] Pass filter state to TransactionTable
- [ ] Update API calls with filter params
- [ ] Sync filters with URL query params
- [ ] Handle filter changes

**Acceptance Criteria:**
- Filters apply to transactions
- URL updates with filters
- Table refreshes on filter change

---

## Phase 6: Transaction Matching UI (Priority 3)

### Task 6.1: Match Review Panel - Core
**Estimated Effort:** 1 day  
**Dependencies:** None  
**File:** `frontend/src/components/matching/MatchReviewPanel.tsx`

**Subtasks:**
- [ ] Create component structure
- [ ] Fetch match suggestions from API
- [ ] Display list of matches
- [ ] Show confidence scores
- [ ] Add accept/reject buttons
- [ ] Implement accept/reject API calls
- [ ] Refresh list after action

**Acceptance Criteria:**
- Matches displayed correctly
- Accept/reject buttons work
- List updates after actions

---

### Task 6.2: Match Suggestion Component
**Estimated Effort:** 1 day  
**Dependencies:** Task 6.1  
**File:** `frontend/src/components/matching/MatchSuggestion.tsx`

**Subtasks:**
- [ ] Create side-by-side comparison layout
- [ ] Display both transactions
- [ ] Show match details (date diff, amount, etc.)
- [ ] Add confidence score indicator (color-coded)
- [ ] Add accept/reject buttons
- [ ] Style component

**Acceptance Criteria:**
- Side-by-side comparison clear
- All match details visible
- Confidence score obvious
- Buttons functional

---

### Task 6.3: Unmatched Transactions View
**Estimated Effort:** 1 day  
**Dependencies:** None  
**File:** `frontend/src/components/matching/UnmatchedTransactions.tsx`

**Subtasks:**
- [ ] Create component
- [ ] Fetch unmatched transactions from API
- [ ] Group by transaction type
- [ ] Add manual match search
- [ ] Add run matching algorithm button
- [ ] Display transactions in table

**Acceptance Criteria:**
- Unmatched transactions displayed
- Grouped correctly
- Manual match search works
- Run algorithm button functional

---

## Phase 7: Visualization (Priority 4)

### Task 7.1: Visualization API - Income/Expense Endpoint
**Estimated Effort:** 1 day  
**Dependencies:** None  
**File:** `backend/src/api/routes/visualization.py`

**Subtasks:**
- [ ] Create route file
- [ ] Implement income/expense aggregation query
- [ ] Group by category
- [ ] Support date range filtering
- [ ] Format response for frontend
- [ ] Add error handling

**Acceptance Criteria:**
- Endpoint returns correct data
- Date filtering works
- Response format matches spec

---

### Task 7.2: Visualization API - Expense Over Time Endpoint
**Estimated Effort:** 1 day  
**Dependencies:** None  
**File:** `backend/src/api/routes/visualization.py`

**Subtasks:**
- [ ] Implement time-based aggregation
- [ ] Support monthly/quarterly/yearly periods
- [ ] Stack by expense subcategory
- [ ] Format response for stacked chart

**Acceptance Criteria:**
- Time periods aggregated correctly
- Stacked data format correct

---

### Task 7.3: Visualization API - Balance Sheet Endpoint
**Estimated Effort:** 1 day  
**Dependencies:** None  
**File:** `backend/src/api/routes/visualization.py`

**Subtasks:**
- [ ] Implement asset/liability/equity aggregation
- [ ] Calculate net worth
- [ ] Monthly aggregation
- [ ] Format for line chart

**Acceptance Criteria:**
- All three metrics calculated
- Net worth included
- Monthly data correct

---

### Task 7.4: Income/Expense Chart Component
**Estimated Effort:** 1 day  
**Dependencies:** Task 7.1  
**File:** `frontend/src/components/visualization/IncomeExpenseChart.tsx`

**Subtasks:**
- [ ] Install chart library (Chart.js or Plotly)
- [ ] Create horizontal bar chart
- [ ] Fetch data from API
- [ ] Format data for chart
- [ ] Add hover tooltips
- [ ] Add export functionality
- [ ] Style chart

**Acceptance Criteria:**
- Chart displays correctly
- Tooltips show on hover
- Export works

---

### Task 7.5: Expense Over Time Chart Component
**Estimated Effort:** 1.5 days  
**Dependencies:** Task 7.2  
**File:** `frontend/src/components/visualization/ExpenseOverTimeChart.tsx`

**Subtasks:**
- [ ] Create stacked bar chart
- [ ] Fetch data from API
- [ ] Add time period selector
- [ ] Add category toggle
- [ ] Add hover tooltips
- [ ] Style chart

**Acceptance Criteria:**
- Stacked chart displays
- Time period changes work
- Categories toggleable

---

### Task 7.6: Balance Sheet Chart Component
**Estimated Effort:** 1 day  
**Dependencies:** Task 7.3  
**File:** `frontend/src/components/visualization/BalanceSheetChart.tsx`

**Subtasks:**
- [ ] Create multi-line chart
- [ ] Fetch data from API
- [ ] Display Asset, Liability, Equity lines
- [ ] Add net worth line
- [ ] Add line toggle
- [ ] Style chart

**Acceptance Criteria:**
- All lines display
- Toggle works
- Net worth calculated

---

### Task 7.7: Dashboard Integration
**Estimated Effort:** 0.5 days  
**Dependencies:** All chart components  
**File:** `frontend/src/pages/Dashboard.tsx`

**Subtasks:**
- [ ] Add charts to dashboard layout
- [ ] Add date range selector for all charts
- [ ] Handle chart refresh on data update
- [ ] Responsive grid layout

**Acceptance Criteria:**
- Charts display on dashboard
- Date range applies to all
- Layout responsive

---

## Phase 8: Export Functionality (Priority 5)

### Task 8.1: Export API - CSV Endpoint
**Estimated Effort:** 1 day  
**Dependencies:** None  
**File:** `backend/src/api/routes/export.py`

**Subtasks:**
- [ ] Create export route file
- [ ] Implement CSV generation
- [ ] Support column selection
- [ ] Apply filters
- [ ] Stream large files
- [ ] Set proper headers

**Acceptance Criteria:**
- CSV exports correctly
- Columns configurable
- Filters applied

---

### Task 8.2: Export API - Excel Endpoint
**Estimated Effort:** 2 days  
**Dependencies:** None  
**File:** `backend/src/api/routes/export.py`

**Subtasks:**
- [ ] Install Excel library (openpyxl)
- [ ] Create multiple sheets
- [ ] Format cells
- [ ] Add summary sheet
- [ ] Add trial balance sheet

**Acceptance Criteria:**
- Excel file generated
- Multiple sheets present
- Formatting applied

---

### Task 8.3: Export API - PDF Endpoint
**Estimated Effort:** 2 days  
**Dependencies:** None  
**File:** `backend/src/api/routes/export.py`

**Subtasks:**
- [ ] Install PDF library (reportlab)
- [ ] Create report layout
- [ ] Add charts/images
- [ ] Handle pagination
- [ ] Add branding

**Acceptance Criteria:**
- PDF generated
- Layout professional
- Charts embedded

---

### Task 8.4: Export Dialog Component
**Estimated Effort:** 1 day  
**Dependencies:** None  
**File:** `frontend/src/components/export/ExportDialog.tsx`

**Subtasks:**
- [ ] Create modal dialog
- [ ] Add format selection
- [ ] Add export options
- [ ] Show preview
- [ ] Implement download
- [ ] Show progress

**Acceptance Criteria:**
- Dialog opens correctly
- Options selectable
- Download works

---

## Summary

**Total Tasks:** ~50 tasks  
**Total Estimated Effort:** ~50-60 days (10-12 weeks with 1 developer)  
**Critical Path:** Phase 4 → Phase 5 → Phase 6 → Phase 7 → Phase 8

**Priority Focus:**
- **Weeks 1-3:** Phase 4 (Transaction Management)
- **Weeks 4-5:** Phase 5 (Filtering)
- **Weeks 6-7:** Phase 6 (Matching UI)
- **Weeks 8-10:** Phase 7 (Visualization)
- **Weeks 11-12:** Phase 8 (Export)

---

**Last Updated:** January 2025

