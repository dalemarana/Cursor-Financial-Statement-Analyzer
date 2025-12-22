---
name: "Priority 4: Visualization API Endpoints"
about: Implement backend API endpoints for chart data generation
title: "[Priority 4] Visualization API Endpoints"
labels: ["priority-4", "backend", "feature", "phase-7"]
assignees: []
---

## Overview
Create backend API endpoints that generate data for the three main visualizations: income/expense chart, expense over time chart, and balance sheet chart.

## Description
The frontend needs API endpoints that aggregate transaction data and return it in a format suitable for chart libraries.

## Acceptance Criteria
- [ ] `GET /api/visualization/income-expense` endpoint
  - [ ] Returns income and expense totals by category
  - [ ] Supports date range filtering
  - [ ] Returns data in chart-friendly format
- [ ] `GET /api/visualization/expense-over-time` endpoint
  - [ ] Returns expense totals grouped by time period (month/quarter/year)
  - [ ] Stacked by expense subcategory
  - [ ] Supports date range filtering
  - [ ] Configurable time period (monthly/quarterly/yearly)
- [ ] `GET /api/visualization/balance-sheet` endpoint
  - [ ] Returns Asset, Liability, and Equity totals over time
  - [ ] Monthly aggregation
  - [ ] Supports date range filtering
  - [ ] Includes net worth calculation (Assets - Liabilities)

## Technical Requirements
- **Files:** 
  - `backend/src/api/routes/visualization.py` - New route file
  - `backend/src/api/schemas.py` - Response schemas
- **Dependencies:** SQLAlchemy for aggregation queries
- **Performance:** Optimized queries with proper indexing
- **Caching:** Consider caching for expensive aggregations

## API Response Format Examples

### Income/Expense
```json
{
  "income": [
    {"category": "Salary", "amount": 5000},
    {"category": "Interest Income", "amount": 100}
  ],
  "expenses": [
    {"category": "Food & Dining", "amount": 500},
    {"category": "Transportation", "amount": 200}
  ],
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-12-31"
  }
}
```

### Expense Over Time
```json
{
  "periods": ["2024-01", "2024-02", "2024-03"],
  "data": {
    "Food & Dining": [500, 450, 600],
    "Transportation": [200, 180, 220],
    "Utilities": [150, 150, 150]
  },
  "period_type": "monthly"
}
```

### Balance Sheet
```json
{
  "periods": ["2024-01", "2024-02", "2024-03"],
  "assets": [10000, 10500, 11000],
  "liabilities": [2000, 1800, 1600],
  "equity": [8000, 8700, 9400],
  "net_worth": [8000, 8700, 9400]
}
```

## Query Optimization
- Use database aggregation functions (SUM, GROUP BY)
- Ensure proper indexes on date, category, and transaction_type columns
- Consider materialized views for complex aggregations
- Implement pagination if data becomes large

## Error Handling
- Validate date range parameters
- Handle empty result sets gracefully
- Return appropriate HTTP status codes
- Provide error messages for invalid parameters

## Related Files
- `backend/src/api/routes/transactions.py` - Reference for query patterns
- `backend/src/database/models.py` - Transaction model
- Frontend visualization components (separate issues)

## Dependencies
- Database indexes on transaction columns
- Date filtering logic (may reuse from transactions endpoint)

## Estimated Effort
**3-4 days**

## Priority
**P4 - Medium** (Required for Phase 7)

---
**Related Issues:**
- Income/Expense Chart Component
- Expense Over Time Chart Component
- Balance Sheet Chart Component

