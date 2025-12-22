# Financial Statement Analyzer - Implementation Plan

## Multi-User Bank Statement Processing & Analysis System

**Version:** 2.0 (Finalized)  
**Date:** January 2025  
**Status:** Ready for Implementation

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Features](#core-features)
3. [User Authentication & Multi-User Support](#user-authentication--multi-user-support)
4. [Data Processing Pipeline](#data-processing-pipeline)
5. [Categorization System](#categorization-system)
6. [Balance Validation](#balance-validation)
7. [Filtering & Search](#filtering--search)
8. [Visualization](#visualization)
9. [Export Functionality](#export-functionality)
10. [Web Application Structure](#web-application-structure)
11. [API Endpoints](#api-endpoints)
12. [Database Schema](#database-schema)
13. [Implementation Phases](#implementation-phases)
14. [Technology Stack](#technology-stack)

---

## Architecture Overview

### Layered Architecture (Web + CLI Ready)

```markdown:IMPLEMENTATION_PLAN.md

```

┌─────────────────────────────────────────────────────────┐
│ Presentation Layer │
│ - Web UI (React/TypeScript) │
│ - CLI Interface (Future) │
├─────────────────────────────────────────────────────────┤
│ API Layer (FastAPI) │
│ - Authentication & Authorization │
│ - RESTful Endpoints │
│ - Request Validation │
├─────────────────────────────────────────────────────────┤
│ Business Logic Layer │
│ - Transaction Matching │
│ - Categorization Engine │
│ - Balance Validation │
│ - Learning System │
├─────────────────────────────────────────────────────────┤
│ Data Processing Layer │
│ - PDF Parser │
│ - Account Detection │
│ - Data Transformation │
├─────────────────────────────────────────────────────────┤
│ Data Storage Layer │
│ - PostgreSQL Database │
│ - File Storage (S3/Local) │
│ - Learning Data Cache │
└─────────────────────────────────────────────────────────┘

```

### Design Principles
- **Separation of Concerns**: Each layer is independent and testable
- **Reusability**: Core logic can be used by both web and CLI
- **Scalability**: Multi-user support with proper data isolation
- **Extensibility**: Easy to add new features and bank formats

---

## Core Features

### 1. PDF Statement Parsing
- Support for multiple bank formats (HSBC, AMEX, NatWest, Barclays)
- Extract: date, amount, description, balance, transaction type
- Handle both credit and debit card statements
- Error handling for corrupted or unsupported formats

### 2. Transaction Matching
- Match transactions across multiple statements
- Criteria: Amount (exact) + Date (±2 days tolerance)
- Confidence scoring for matches
- User review and confirmation interface
- Handle unmatched transactions with suggestions

### 3. Account Detection
- Auto-detect account names from transaction descriptions
- Pattern matching for common account types
- User override and manual mapping capability
- Account hierarchy support (parent/child accounts)

### 4. Categorization
- Financial components: Asset, Liability, Equity, Income, Expense
- Subcategory support (user-defined)
- Bulk assignment by vendor/pattern
- Machine learning-based suggestions
- User confirmation and override capability

### 5. Balance Validation
- Trial balance check: Assets + Expenses = Liabilities + Equity + Income
- Individual account reconciliation
- Discrepancy detection and reporting
- Actionable suggestions for fixing imbalances

### 6. Filtering & Search
- Date range filtering
- Category/subcategory filtering
- Account filtering
- Amount range filtering
- Transaction type filtering (Paid In/Paid Out)
- Text search in descriptions
- Vendor/merchant filtering
- Match status filtering (matched/unmatched)

### 7. Visualization
- Income/Expense horizontal bar chart
- Expense type stacked bar chart over time
- Asset/Liability/Equity line graph
- Interactive charts with drill-down capability
- Export charts as images

### 8. Export Functionality
- CSV export (transactions, categories, balance reports)
- Excel export with multiple sheets
- PDF reports (financial statements, summaries)
- JSON export (for data portability)
- Chart/image export (PNG, SVG, PDF)

---

## User Authentication & Multi-User Support

### Authentication System
**Location:** `src/auth/`

#### Components:
1. **User Registration & Login**
   - Email/password authentication
   - Password hashing (bcrypt)
   - JWT token-based session management
   - Password reset functionality
   - Email verification (optional)

2. **Authorization**
   - Role-based access control (RBAC)
   - User data isolation (users can only access their own data)
   - API endpoint protection
   - File upload restrictions per user

3. **Session Management**
   - JWT tokens with expiration
   - Refresh token mechanism
   - Secure cookie handling
   - Logout functionality

**Key Files:**
- `src/auth/authentication.py` - Login, registration, token generation
- `src/auth/authorization.py` - Permission checks, RBAC
- `src/auth/middleware.py` - Request authentication middleware
- `src/auth/schemas.py` - Pydantic models for auth

**Database Tables:**
- `users` - User accounts
- `sessions` - Active user sessions
- `user_preferences` - User settings and preferences

---

## Data Processing Pipeline

### Phase 1: Upload & Parse
1. User uploads PDF statement(s)
2. File validation (format, size, security scan)
3. Store file in user's directory/S3 bucket
4. Extract text from PDF
5. Parse transactions using bank-specific parsers
6. Standardize transaction format
7. Store raw transactions in database

### Phase 2: Account Detection
1. Analyze transaction descriptions
2. Extract account names using pattern matching
3. Match against known accounts or create new ones
4. User review and confirmation

### Phase 3: Transaction Matching
1. Group transactions by user and date range
2. Match "Paid Out" with "Paid In" transactions
3. Calculate match confidence scores
4. Flag unmatched transactions
5. Generate match suggestions
6. User review and confirmation interface

### Phase 4: Categorization
1. Apply learning engine suggestions
2. Apply bulk assignment rules
3. Present suggestions to user
4. Allow user to override and confirm
5. Learn from user decisions
6. Update learning database

### Phase 5: Validation
1. Calculate trial balance
2. Reconcile individual accounts
3. Detect discrepancies
4. Generate error reports
5. Provide fix suggestions

---

## Categorization System

### Category Structure
```

Financial Components:
├── Asset
│ ├── Cash
│ ├── Bank Accounts
│ ├── Investments
│ └── [User-defined subcategories]
├── Liability
│ ├── Credit Cards
│ ├── Loans
│ ├── Accounts Payable
│ └── [User-defined subcategories]
├── Equity
│ ├── Capital
│ ├── Retained Earnings
│ └── [User-defined subcategories]
├── Income
│ ├── Salary
│ ├── Interest Income
│ ├── Other Income
│ └── [User-defined subcategories]
└── Expense
├── Utilities
├── Food & Dining
├── Transportation
└── [User-defined subcategories]

````

### Learning Engine
**Location:** `src/categorization/learning_engine.py`

**Features:**
- Vendor/merchant pattern matching
- Keyword-based categorization
- Amount-based rules (e.g., large amounts → specific category)
- Frequency-based learning (most common category for vendor)
- Confidence scoring
- User-specific learning (per-user patterns)

**Data Storage:**
- Per-user learning patterns (stored in database)
- Global patterns (optional, for new users)
- Pattern confidence scores
- Usage statistics

**Key Functions:**
```python
def suggest_category(transaction: Transaction, user_id: str) -> CategorySuggestion
def learn_from_assignment(transaction: Transaction, category: str, user_id: str)
def bulk_assign_by_vendor(vendor_pattern: str, category: str, user_id: str)
def get_category_confidence(transaction: Transaction, category: str, user_id: str) -> float
````

---

## Balance Validation

### Trial Balance Check

**Formula:** Assets + Expenses = Liabilities + Equity + Income

**Implementation:**

- Calculate totals for each component
- Compare left side vs right side
- Flag discrepancies with amount and percentage
- Provide suggestions:
  - Missing transactions
  - Incorrect categorizations
  - Unmatched transactions affecting balance

### Account Reconciliation

- Compare statement ending balance with calculated balance
- Identify missing transactions
- Flag timing differences
- Generate reconciliation report

**Error Messages:**

- "Trial balance is off by $XXX.XX (X.XX%)"
- "Account 'Checking' has $XXX.XX discrepancy"
- "X transactions are unmatched and may affect balance"
- "Suggested fixes: [list of actionable items]"

---

## Filtering & Search

### Available Filters

1. **Date Range Filter**

   - Start date / End date picker
   - Preset ranges: This Month, Last Month, This Year, Custom
   - Time zone handling

2. **Category Filter**

   - Multi-select dropdown
   - Filter by main category (Asset, Liability, etc.)
   - Filter by subcategory
   - "Uncategorized" option

3. **Account Filter**

   - Multi-select dropdown
   - Filter by account name
   - Filter by account type

4. **Amount Range Filter**

   - Min amount / Max amount
   - Slider interface
   - Preset ranges: <$100, $100-$500, >$500

5. **Transaction Type Filter**

   - Paid In / Paid Out / Both
   - Toggle buttons

6. **Match Status Filter**

   - Matched / Unmatched / Pending Review
   - Toggle buttons

7. **Text Search**

   - Search in description
   - Search in vendor/merchant name
   - Case-insensitive
   - Partial matching

8. **Vendor/Merchant Filter**
   - Auto-complete dropdown
   - Most frequent vendors shown first
   - Multi-select capability

### Filter Combination

- All filters can be combined (AND logic)
- Save filter presets for quick access
- Clear all filters button
- Filter count indicator

### Implementation

**Location:** `src/filters/query_builder.py`

```python
class TransactionFilter:
    date_range: Optional[DateRange]
    categories: List[str]
    accounts: List[str]
    amount_range: Optional[AmountRange]
    transaction_types: List[str]
    match_status: Optional[str]
    search_text: Optional[str]
    vendors: List[str]

def build_query(filters: TransactionFilter, user_id: str) -> Query
```

---

## Visualization

### Graph 1: Income/Expense Horizontal Bar Chart

- **Type:** Horizontal grouped bar chart
- **X-axis:** Amount (currency)
- **Y-axis:** Categories (Income categories vs Expense categories)
- **Colors:** Green (Income), Red (Expense)
- **Features:**
  - Hover tooltips with exact amounts
  - Click to drill down to transactions
  - Export as image
  - Date range filtering

### Graph 2: Expense Type Stacked Bar Chart

- **Type:** Stacked bar chart
- **X-axis:** Time (monthly/quarterly)
- **Y-axis:** Amount (currency)
- **Stack:** Expense subcategories
- **Colors:** Different color per subcategory
- **Features:**
  - Legend with subcategories
  - Toggle subcategories on/off
  - Hover for breakdown
  - Time period selector (Monthly/Quarterly/Yearly)

### Graph 3: Asset/Liability/Equity Line Graph

- **Type:** Multi-line chart
- **X-axis:** Time (monthly)
- **Y-axis:** Amount (currency)
- **Lines:** Asset, Liability, Equity (separate lines)
- **Colors:** Blue (Asset), Red (Liability), Green (Equity)
- **Features:**
  - Toggle lines on/off
  - Show net worth line (Assets - Liabilities)
  - Hover for exact values
  - Trend indicators

### Implementation

**Location:** `src/visualization/graph_generator.py`

**Backend:** Generate data in format suitable for frontend
**Frontend:** Use Chart.js or Plotly.js for rendering

---

## Export Functionality

### Export Formats

#### 1. CSV Export

- **File:** `transactions_export_YYYYMMDD.csv`
- **Columns:** Date, Description, Amount, Type, Account, Category, Subcategory, Matched Status
- **Options:**
  - Include/exclude columns
  - Apply current filters
  - Date range selection

#### 2. Excel Export

- **File:** `financial_report_YYYYMMDD.xlsx`
- **Sheets:**
  - Transactions (detailed)
  - Summary by Category
  - Trial Balance
  - Account Reconciliation
  - Charts (embedded)
- **Options:**
  - Include charts
  - Apply filters
  - Custom date range

#### 3. PDF Export

- **File:** `financial_statement_YYYYMMDD.pdf`
- **Contents:**
  - Cover page
  - Executive summary
  - Transaction list (paginated)
  - Charts and visualizations
  - Balance reports
- **Options:**
  - Include/exclude sections
  - Date range
  - Custom branding

#### 4. JSON Export

- **File:** `data_export_YYYYMMDD.json`
- **Structure:** Complete data model including:
  - Transactions
  - Categories
  - Accounts
  - Matches
  - Learning patterns
- **Use case:** Data portability, backup, migration

#### 5. Chart Export

- **Formats:** PNG, SVG, PDF
- **Options:**
  - Resolution/quality
  - Background color
  - Include legend
  - Custom dimensions

### Implementation

**Location:** `src/export/export_manager.py`

**Key Functions:**

```python
def export_csv(transactions: List[Transaction], filters: TransactionFilter) -> BytesIO
def export_excel(transactions: List[Transaction], charts: List[Chart], filters: TransactionFilter) -> BytesIO
def export_pdf(report_data: ReportData, filters: TransactionFilter) -> BytesIO
def export_json(user_data: UserData) -> dict
def export_chart(chart: Chart, format: str) -> BytesIO
```

---

## Web Application Structure

### Frontend Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── auth/
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   └── PasswordReset.tsx
│   │   ├── upload/
│   │   │   ├── FileUpload.tsx
│   │   │   └── UploadProgress.tsx
│   │   ├── transactions/
│   │   │   ├── TransactionTable.tsx
│   │   │   ├── TransactionRow.tsx
│   │   │   ├── CategoryDropdown.tsx
│   │   │   └── BulkEditPanel.tsx
│   │   ├── matching/
│   │   │   ├── MatchReviewPanel.tsx
│   │   │   ├── MatchSuggestion.tsx
│   │   │   └── UnmatchedTransactions.tsx
│   │   ├── filters/
│   │   │   ├── FilterPanel.tsx
│   │   │   ├── DateRangePicker.tsx
│   │   │   └── FilterPresets.tsx
│   │   ├── validation/
│   │   │   ├── BalanceAlert.tsx
│   │   │   ├── TrialBalanceReport.tsx
│   │   │   └── ReconciliationReport.tsx
│   │   ├── visualization/
│   │   │   ├── IncomeExpenseChart.tsx
│   │   │   ├── ExpenseOverTimeChart.tsx
│   │   │   ├── BalanceSheetChart.tsx
│   │   │   └── ChartExport.tsx
│   │   ├── export/
│   │   │   ├── ExportDialog.tsx
│   │   │   └── ExportOptions.tsx
│   │   └── layout/
│   │       ├── Navbar.tsx
│   │       ├── Sidebar.tsx
│   │       └── Dashboard.tsx
│   ├── services/
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   └── storage.ts
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useTransactions.ts
│   │   └── useFilters.ts
│   ├── utils/
│   │   ├── formatters.ts
│   │   └── validators.ts
│   └── App.tsx
├── package.json
└── tsconfig.json
```

### Backend Structure

```
backend/
├── src/
│   ├── auth/
│   │   ├── authentication.py
│   │   ├── authorization.py
│   │   └── middleware.py
│   ├── parsers/
│   │   ├── pdf_parser.py
│   │   └── statement_parser.py
│   ├── matching/
│   │   ├── transaction_matcher.py
│   │   └── match_validator.py
│   ├── accounts/
│   │   └── account_detector.py
│   ├── categorization/
│   │   ├── category_manager.py
│   │   ├── learning_engine.py
│   │   └── bulk_assigner.py
│   ├── validation/
│   │   ├── trial_balance.py
│   │   └── account_reconciliation.py
│   ├── filters/
│   │   └── query_builder.py
│   ├── visualization/
│   │   └── graph_generator.py
│   ├── export/
│   │   └── export_manager.py
│   ├── models/
│   │   ├── transaction.py
│   │   ├── user.py
│   │   └── category.py
│   ├── database/
│   │   ├── models.py (SQLAlchemy)
│   │   ├── connection.py
│   │   └── migrations/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── transactions.py
│   │   │   ├── categories.py
│   │   │   ├── matching.py
│   │   │   ├── validation.py
│   │   │   ├── visualization.py
│   │   │   └── export.py
│   │   └── schemas.py
│   └── main.py
├── requirements.txt
└── alembic.ini
```

---

## API Endpoints

### Authentication Endpoints

```
POST   /api/auth/register          # User registration
POST   /api/auth/login             # User login
POST   /api/auth/logout            # User logout
POST   /api/auth/refresh          # Refresh JWT token
POST   /api/auth/password-reset   # Request password reset
POST   /api/auth/verify-email     # Email verification
GET    /api/auth/me               # Get current user info
```

### Transaction Endpoints

```
POST   /api/transactions/upload           # Upload PDF statements
GET    /api/transactions                 # Get transactions (with filters)
GET    /api/transactions/{id}            # Get single transaction
PUT    /api/transactions/{id}            # Update transaction
PUT    /api/transactions/{id}/category   # Update category
POST   /api/transactions/bulk-update     # Bulk update transactions
DELETE /api/transactions/{id}            # Delete transaction
GET    /api/transactions/stats           # Get transaction statistics
```

### Matching Endpoints

```
POST   /api/matching/match               # Run matching algorithm
GET    /api/matching/suggestions         # Get match suggestions
POST   /api/matching/confirm/{match_id}  # Confirm a match
POST   /api/matching/reject/{match_id}   # Reject a match
GET    /api/matching/unmatched           # Get unmatched transactions
```

### Category Endpoints

```
GET    /api/categories                   # Get all categories
POST   /api/categories                   # Create category/subcategory
PUT    /api/categories/{id}              # Update category
DELETE /api/categories/{id}              # Delete category
POST   /api/categories/bulk-assign       # Bulk category assignment
GET    /api/categories/suggestions       # Get category suggestions
```

### Account Endpoints

```
GET    /api/accounts                     # Get all accounts
POST   /api/accounts                     # Create account
PUT    /api/accounts/{id}                # Update account
DELETE /api/accounts/{id}                # Delete account
POST   /api/accounts/detect              # Auto-detect account names
```

### Validation Endpoints

```
GET    /api/validation/trial-balance     # Get trial balance
GET    /api/validation/reconcile         # Reconcile accounts
GET    /api/validation/discrepancies     # Get discrepancies
POST   /api/validation/fix-suggestion    # Apply fix suggestion
```

### Visualization Endpoints

```
GET    /api/visualization/income-expense        # Income/expense data
GET    /api/visualization/expense-over-time     # Expense over time data
GET    /api/visualization/balance-sheet         # Balance sheet data
```

### Export Endpoints

```
POST   /api/export/csv                  # Export as CSV
POST   /api/export/excel                # Export as Excel
POST   /api/export/pdf                  # Export as PDF
POST   /api/export/json                 # Export as JSON
POST   /api/export/chart                # Export chart as image
```

### Filter Endpoints

```
GET    /api/filters/presets             # Get saved filter presets
POST   /api/filters/presets             # Save filter preset
DELETE /api/filters/presets/{id}        # Delete filter preset
```

---

## Database Schema

### Core Tables

#### users

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### statements

```sql
CREATE TABLE statements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    bank_name VARCHAR(100),
    account_type VARCHAR(50),
    statement_date_start DATE,
    statement_date_end DATE,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    parsed_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'uploaded'
);
```

#### transactions

```sql
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    statement_id UUID REFERENCES statements(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    description TEXT,
    transaction_type VARCHAR(20) NOT NULL, -- 'Paid In' or 'Paid Out'
    account_name VARCHAR(255),
    balance DECIMAL(15, 2),
    category VARCHAR(50),
    subcategory VARCHAR(100),
    matched_transaction_id UUID REFERENCES transactions(id),
    match_confidence DECIMAL(5, 2),
    is_confirmed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### accounts

```sql
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    account_type VARCHAR(50),
    parent_account_id UUID REFERENCES accounts(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### categories

```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    parent_category VARCHAR(50), -- Asset, Liability, Equity, Income, Expense
    subcategory VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### learning_patterns

```sql
CREATE TABLE learning_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    pattern_type VARCHAR(50), -- 'vendor', 'keyword', 'amount_range'
    pattern_value VARCHAR(255),
    category_id UUID REFERENCES categories(id),
    confidence DECIMAL(5, 2),
    usage_count INTEGER DEFAULT 1,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### filter_presets

```sql
CREATE TABLE filter_presets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    filter_config JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### sessions

```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes

```sql
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_transactions_category ON transactions(category);
CREATE INDEX idx_transactions_account ON transactions(account_name);
CREATE INDEX idx_transactions_matched ON transactions(matched_transaction_id);
CREATE INDEX idx_statements_user_id ON statements(user_id);
CREATE INDEX idx_learning_patterns_user ON learning_patterns(user_id, pattern_type);
```

---

## Implementation Phases

### Phase 1: Foundation & Authentication (Weeks 1-2)

**Goals:**

- Set up project structure
- Database setup and migrations
- User authentication system
- Basic API framework

**Deliverables:**

- User registration/login working
- Database schema implemented
- Basic API structure
- Authentication middleware

### Phase 2: PDF Parsing & Data Models (Weeks 3-4)

**Goals:**

- Integrate/refactor existing PDF parser
- Create transaction data models
- File upload functionality
- Basic transaction storage

**Deliverables:**

- PDF parser working for all supported banks
- Transaction extraction and storage
- File upload API endpoint
- Transaction CRUD operations

### Phase 3: Transaction Matching (Weeks 5-6)

**Goals:**

- Build matching algorithm
- Account detection
- Match suggestion system
- User review interface

**Deliverables:**

- Matching engine working
- Account auto-detection
- Match suggestions API
- Frontend match review panel

### Phase 4: Categorization System (Weeks 7-8)

**Goals:**

- Category management
- Learning engine
- Bulk assignment
- User interface for categorization

**Deliverables:**

- Category CRUD operations
- Learning system storing patterns
- Bulk assignment functionality
- Category dropdown in transaction table

### Phase 5: Validation & Balance Checks (Weeks 9-10)

**Goals:**

- Trial balance calculation
- Account reconciliation
- Discrepancy detection
- Error reporting

**Deliverables:**

- Trial balance API
- Reconciliation reports
- Discrepancy alerts
- Fix suggestion system

### Phase 6: Filtering & Search (Week 11)

**Goals:**

- Implement all filter types
- Filter combination logic
- Filter presets
- Search functionality

**Deliverables:**

- Complete filtering system
- Filter UI components
- Saved filter presets
- Search functionality

### Phase 7: Visualization (Weeks 12-13)

**Goals:**

- Generate graph data
- Create chart components
- Interactive features
- Chart export

**Deliverables:**

- All three graph types working
- Interactive charts
- Chart export functionality
- Dashboard layout

### Phase 8: Export Functionality (Week 14)

**Goals:**

- CSV export
- Excel export
- PDF export
- JSON export
- Chart image export

**Deliverables:**

- All export formats working
- Export options UI
- File download functionality

### Phase 9: Testing & Polish (Weeks 15-16)

**Goals:**

- End-to-end testing
- Performance optimization
- Error handling
- Documentation
- Security audit

**Deliverables:**

- Test suite
- Performance benchmarks
- User documentation
- API documentation
- Security review

---

## Technology Stack

### Backend

- **Framework:** FastAPI (Python 3.10+)
- **Database:** PostgreSQL 14+
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Authentication:** JWT (python-jose), bcrypt
- **PDF Parsing:** pdfplumber, PyPDF2 (extend existing parser)
- **File Storage:** Local filesystem (dev) / AWS S3 (production)
- **Task Queue:** Celery + Redis (for async processing)
- **Validation:** Pydantic

### Frontend

- **Framework:** React 18+ with TypeScript
- **State Management:** React Query / Zustand
- **UI Library:** Material-UI or Ant Design
- **Charts:** Chart.js or Plotly.js
- **Forms:** React Hook Form
- **Date Picker:** react-datepicker
- **File Upload:** react-dropzone
- **HTTP Client:** Axios

### Development Tools

- **Package Manager:** pip (backend), npm/yarn (frontend)
- **Code Quality:** Black, flake8, mypy (backend)
- **Testing:** pytest (backend), Jest + React Testing Library (frontend)
- **CI/CD:** GitHub Actions
- **Containerization:** Docker, Docker Compose

### Deployment

- **Backend:** Docker container on cloud (AWS/GCP/Azure)
- **Frontend:** Static hosting (Vercel/Netlify) or CDN
- **Database:** Managed PostgreSQL (AWS RDS, etc.)
- **File Storage:** AWS S3 or similar

---

## Security Considerations

1. **Authentication Security**

   - Password hashing with bcrypt (cost factor 12+)
   - JWT tokens with short expiration
   - Refresh token rotation
   - Rate limiting on login endpoints

2. **Data Security**

   - User data isolation (enforced at database level)
   - File upload validation (type, size, content scan)
   - SQL injection prevention (parameterized queries)
   - XSS prevention (input sanitization)

3. **API Security**

   - HTTPS only
   - CORS configuration
   - API rate limiting
   - Request validation

4. **File Security**
   - Secure file storage
   - Access control on files
   - Virus scanning (optional)
   - File size limits

---

## Performance Considerations

1. **Database Optimization**

   - Proper indexing
   - Query optimization
   - Connection pooling
   - Read replicas for scaling

2. **Caching**

   - Redis for session storage
   - Cache frequently accessed data
   - Cache visualization data

3. **Async Processing**

   - Background tasks for PDF parsing
   - Async matching algorithm
   - Queue system for heavy operations

4. **Frontend Optimization**
   - Code splitting
   - Lazy loading
   - Virtual scrolling for large tables
   - Memoization

---

## Future Enhancements (Post-MVP)

1. **CLI Version**

   - Reuse core logic modules
   - Command-line interface
   - Batch processing
   - Script automation

2. **Advanced Features**

   - AI-powered categorization
   - Receipt OCR and matching
   - Budget planning
   - Financial forecasting
   - Multi-currency support
   - Bank API integration

3. **Collaboration**

   - Shared accounts
   - Team workspaces
   - Role-based permissions

4. **Mobile App**
   - React Native app
   - Mobile-optimized UI
   - Push notifications

---

## Success Metrics

1. **Functionality**

   - 95%+ accurate transaction extraction
   - 90%+ match accuracy
   - <5% false positive categorizations

2. **Performance**

   - PDF parsing: <10 seconds per statement
   - Matching: <30 seconds for 1000 transactions
   - Page load: <2 seconds

3. **User Experience**
   - <3 clicks to categorize transaction
   - Intuitive UI (user testing feedback)
   - Export time: <5 seconds

---

## Documentation Requirements

1. **User Documentation**

   - Getting started guide
   - Feature documentation
   - FAQ
   - Video tutorials

2. **Developer Documentation**

   - API documentation (OpenAPI/Swagger)
   - Code comments
   - Architecture diagrams
   - Setup instructions

3. **Admin Documentation**
   - Deployment guide
   - Monitoring setup
   - Troubleshooting guide

---

## Risk Mitigation

1. **PDF Parsing Failures**

   - Fallback parsers
   - Manual entry option
   - Error reporting

2. **Matching Accuracy**

   - User review required
   - Confidence thresholds
   - Manual override

3. **Data Loss**

   - Regular backups
   - Export functionality
   - Version control

4. **Scalability**
   - Horizontal scaling design
   - Database optimization
   - Caching strategy

---

## Conclusion

This implementation plan provides a comprehensive roadmap for building a multi-user financial statement analyzer with all requested features. The architecture is designed to be modular, scalable, and reusable for both web and CLI implementations.

**Next Steps:**

1. Review and approve this plan
2. Set up development environment
3. Initialize project structure
4. Begin Phase 1 implementation

---

**Document Version:** 2.0  
**Last Updated:** January 2025  
**Status:** Finalized and Ready for Implementation

```

You're in ask mode, so I can't save files directly. Save this as `IMPLEMENTATION_PLAN.md` in your project directory. Should I switch to agent mode to create the file, or do you want to save it manually?

The plan includes:
- Multi-user authentication with JWT
- Export (CSV, Excel, PDF, JSON, charts)
- Filtering (date range, category, account, amount, text search, vendor, etc.)
- Database schema for multi-user support
- API endpoints
- Implementation phases with timelines

Should I proceed with any specific phase or adjust anything?
```
