# GitHub Repository Integration Plan

## Overview

This plan outlines the integration of the working bank statement parser from the GitHub repository (`https://github.com/dalemarana/bankStatementParser.git`) into the current FastAPI project.

## Repository Information

- **GitHub URL**: `https://github.com/dalemarana/bankStatementParser.git`
- **Working Code Location**: `/Users/dalemarana/Documents/code_projects/python/BankStatementParser`
- **Main Parser File**: `src/bank_statement_parser/parse_statement_accounts.py`
- **Function**: `parse_bank_statement()`

## Integration Strategy

### Phase 1: Install GitHub Package as Dependency

#### 1.1 Add to requirements.txt

Add the GitHub repository as an editable or direct dependency:

```txt
# Working Bank Statement Parser from GitHub
git+https://github.com/dalemarana/bankStatementParser.git@main#egg=bank-statement-parser
```

**Alternative approach** (if package has setup.py):
```txt
-e git+https://github.com/dalemarana/bankStatementParser.git@main#egg=bank-statement-parser
```

#### 1.2 Install Dependencies

```bash
cd backend
source venv/bin/activate
pip install git+https://github.com/dalemarana/bankStatementParser.git@main
```

#### 1.3 Verify Installation

```bash
python -c "import bank_statement_parser; print(bank_statement_parser.__file__)"
```

### Phase 2: Create Adapter/Wrapper Layer

#### 2.1 Create Adapter Module

**File**: `backend/src/parsers/github_parser_adapter.py`

**Purpose**: Bridge between the GitHub parser (flat list format) and our Transaction model

**Key Functions**:
- Convert flat list `[date, type, details, amount, ...]` to `List[Transaction]`
- Handle date normalization (datetime → date)
- Map transaction types to our format
- Handle errors gracefully

#### 2.2 Integration Points

1. **Import the working parser**:
   ```python
   from bank_statement_parser.parse_statement_accounts import parse_bank_statement
   ```

2. **Create wrapper function**:
   ```python
   def parse_with_github_parser(file_path: str, bank_name: str, 
                                 account_type: str) -> List[Transaction]:
       # Extract parameters from parsing matrix or config
       # Call parse_bank_statement()
       # Convert flat list to Transaction objects
       # Return List[Transaction]
   ```

3. **Update StatementParser**:
   - Add option to use GitHub parser
   - Fallback to GitHub parser if new parser fails
   - Log which parser was used

### Phase 3: Update Current Parser Integration

#### 3.1 Modify `backend/src/parsers/pdf_parser.py`

Add GitHub parser as primary or fallback option:

```python
class StatementParser:
    def __init__(self, use_github_parser: bool = True):
        self.use_github_parser = use_github_parser
        self.github_adapter = GitHubParserAdapter() if use_github_parser else None
        # ... existing initialization
    
    def parse(self, file_path: str, ...) -> List[Transaction]:
        if self.use_github_parser:
            try:
                return self.github_adapter.parse(file_path, bank_name, account_type)
            except Exception as e:
                logger.warning(f"GitHub parser failed: {e}, falling back to new parser")
        
        # Fallback to existing parser
        return self._parse_with_new_parser(file_path, ...)
```

#### 3.2 Update API Route

**File**: `backend/src/api/routes/statements.py`

Ensure it uses the GitHub parser adapter:

```python
from src.parsers.github_parser_adapter import GitHubParserAdapter

# In upload_statement endpoint:
parser_adapter = GitHubParserAdapter()
transactions = parser_adapter.parse(
    file_path=temp_file_path,
    bank_name=bank_name,
    account_type=account_type
)
```

### Phase 4: Configuration & Parameter Mapping

#### 4.1 Parsing Matrix Integration

The GitHub parser requires these parameters:
- `bank`: Bank name (HSBC, AMEX, NatWest, Barclays)
- `year`: Statement year
- `date_pattern`: Date pattern regex
- `paid_in`: List of "Paid In" trigger words
- `paid_out`: List of "Paid Out" trigger words
- `file`: File path
- `folder`: Folder path (optional)
- `test_mode`: Boolean (optional)

#### 4.2 Create Parameter Mapper

**File**: `backend/src/parsers/parameter_mapper.py`

```python
class ParameterMapper:
    def __init__(self, matrix_loader: ParsingMatrixLoader):
        self.matrix_loader = matrix_loader
    
    def get_github_parser_params(self, file_path: str, 
                                  bank_account_name: str,
                                  bank_name: str) -> Dict:
        """Extract parameters needed for GitHub parser from parsing matrix."""
        patterns = self.matrix_loader.get_patterns(bank_account_name)
        
        # Extract year from file or use current year
        year = self._extract_year(file_path)
        
        return {
            'bank': bank_name,
            'year': year,
            'date_pattern': patterns.get('DATE_PATTERN'),
            'paid_in': patterns.get('PAID_IN', []),
            'paid_out': patterns.get('PAID_OUT', []),
            'file': file_path,
            'folder': os.path.dirname(file_path),
            'test_mode': False
        }
```

### Phase 5: Testing Strategy

#### 5.1 Unit Tests

**File**: `backend/tests/test_github_parser_adapter.py`

```python
import pytest
from src.parsers.github_parser_adapter import GitHubParserAdapter

class TestGitHubParserAdapter:
    def test_parse_hsbc_debit_card(self):
        """Test parsing HSBC debit card statement."""
        adapter = GitHubParserAdapter()
        transactions = adapter.parse(
            file_path="test_files/hsbc-debit_card.pdf",
            bank_name="HSBC",
            account_type="debit_card"
        )
        assert len(transactions) > 0
        assert all(t.date is not None for t in transactions)
        assert all(t.amount is not None for t in transactions)
    
    def test_parse_amex_credit_card(self):
        """Test parsing AMEX credit card statement."""
        # Similar test for AMEX
    
    def test_parse_barclays_debit_card(self):
        """Test parsing Barclays debit card statement."""
        # Similar test for Barclays
    
    def test_parse_natwest_debit_card(self):
        """Test parsing NatWest debit card statement."""
        # Similar test for NatWest
    
    def test_conversion_flat_list_to_transactions(self):
        """Test conversion from flat list to Transaction objects."""
        flat_list = [
            datetime(2024, 11, 1), "Paid Out", "Transaction 1", 100.50,
            datetime(2024, 11, 2), "Paid In", "Transaction 2", 200.00
        ]
        adapter = GitHubParserAdapter()
        transactions = adapter._convert_flat_list(flat_list)
        
        assert len(transactions) == 2
        assert transactions[0].transaction_type == "Paid Out"
        assert transactions[0].amount == Decimal("100.50")
```

#### 5.2 Integration Tests

**File**: `backend/tests/test_statement_upload_integration.py`

```python
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

class TestStatementUploadIntegration:
    def test_upload_hsbc_statement(self):
        """Test uploading and parsing HSBC statement via API."""
        with open("test_files/hsbc-debit_card.pdf", "rb") as f:
            response = client.post(
                "/api/statements/upload",
                files={"file": ("hsbc.pdf", f, "application/pdf")},
                data={"account_type": "debit_card"},
                headers={"Authorization": f"Bearer {test_token}"}
            )
        
        assert response.status_code == 201
        data = response.json()
        assert data["transaction_count"] > 0
    
    def test_upload_amex_statement(self):
        """Test uploading and parsing AMEX statement via API."""
        # Similar test
```

#### 5.3 Comparison Tests

**File**: `backend/tests/test_parser_comparison.py`

```python
import pytest
from src.parsers.github_parser_adapter import GitHubParserAdapter
from src.parsers.pdf_parser import StatementParser

class TestParserComparison:
    def test_github_vs_new_parser(self):
        """Compare results from GitHub parser vs new parser."""
        github_adapter = GitHubParserAdapter()
        new_parser = StatementParser(use_github_parser=False)
        
        file_path = "test_files/hsbc-debit_card.pdf"
        
        github_transactions = github_adapter.parse(
            file_path, bank_name="HSBC", account_type="debit_card"
        )
        new_transactions = new_parser.parse(
            file_path, bank_name="HSBC", account_type="debit_card"
        )
        
        # Compare transaction counts
        print(f"GitHub parser: {len(github_transactions)} transactions")
        print(f"New parser: {len(new_transactions)} transactions")
        
        # Compare matched transactions
        matched = self._match_transactions(github_transactions, new_transactions)
        match_rate = len(matched) / max(len(github_transactions), 1)
        
        assert match_rate > 0.9, f"Match rate too low: {match_rate}"
```

#### 5.4 End-to-End Tests

**File**: `backend/tests/test_e2e_workflow.py`

```python
class TestEndToEndWorkflow:
    def test_complete_workflow(self):
        """Test complete workflow: upload → parse → match → categorize."""
        # 1. Upload statement
        # 2. Verify transactions extracted
        # 3. Run matching
        # 4. Verify matches
        # 5. Categorize transactions
        # 6. Verify categorization
        # 7. Check trial balance
        pass
```

#### 5.5 Test Data

**Directory**: `backend/tests/test_files/`

Copy test files from working implementation:
- `hsbc-debit_card.pdf`
- `hsbc-debit_card2.pdf`
- `hsbc-credit_card.pdf`
- `hsbc-credit_card2.pdf`
- `amex-credit_card.pdf`
- `barclays-debit_card.pdf`
- `barclays-debit_card2.pdf`
- `natwest-debit_card.pdf`

### Phase 6: Error Handling & Logging

#### 6.1 Error Handling

```python
class GitHubParserAdapter:
    def parse(self, ...) -> List[Transaction]:
        try:
            flat_list = parse_bank_statement(...)
            return self._convert_flat_list(flat_list)
        except ImportError as e:
            logger.error(f"GitHub parser not installed: {e}")
            raise
        except Exception as e:
            logger.error(f"GitHub parser failed: {e}")
            # Optionally fall back to new parser
            raise
```

#### 6.2 Logging

Add comprehensive logging:
- Which parser is being used
- Number of transactions extracted
- Any warnings or errors
- Performance metrics (parsing time)

### Phase 7: Documentation

#### 7.1 Update README

Add section about GitHub parser integration:
- Installation instructions
- Configuration
- Usage examples

#### 7.2 Code Documentation

- Docstrings for all adapter functions
- Parameter descriptions
- Return type documentation
- Example usage

### Phase 8: Migration Path

#### 8.1 Gradual Migration

1. **Phase 1**: Use GitHub parser as primary, log results
2. **Phase 2**: Compare GitHub vs new parser results
3. **Phase 3**: Fix new parser based on GitHub parser results
4. **Phase 4**: Use new parser as primary, GitHub as fallback
5. **Phase 5**: Remove GitHub parser dependency once new parser matches performance

#### 8.2 Feature Flag

Add configuration option to switch between parsers:

```python
# config.py
USE_GITHUB_PARSER = os.getenv("USE_GITHUB_PARSER", "true").lower() == "true"
```

## Implementation Checklist

### Setup & Installation
- [ ] Add GitHub repository to requirements.txt
- [ ] Install GitHub package in virtual environment
- [ ] Verify installation and imports work
- [ ] Check all dependencies are satisfied

### Code Integration
- [ ] Create `github_parser_adapter.py`
- [ ] Implement flat list to Transaction conversion
- [ ] Create parameter mapper
- [ ] Update StatementParser to use adapter
- [ ] Update API routes to use adapter
- [ ] Add error handling
- [ ] Add logging

### Testing
- [ ] Create unit tests for adapter
- [ ] Create integration tests for API
- [ ] Create comparison tests
- [ ] Create E2E workflow tests
- [ ] Copy test files to test directory
- [ ] Run all tests and verify results
- [ ] Test with all bank types (HSBC, AMEX, NatWest, Barclays)
- [ ] Test with both credit and debit cards

### Documentation
- [ ] Update README with installation instructions
- [ ] Document adapter usage
- [ ] Add code comments and docstrings
- [ ] Create migration guide

### Validation
- [ ] Verify transaction extraction matches working implementation
- [ ] Verify all test files parse correctly
- [ ] Verify API endpoints work with GitHub parser
- [ ] Performance testing (parsing speed)
- [ ] Memory usage testing

## Expected Outcomes

1. **Functional**: All bank statement types parse correctly using GitHub parser
2. **Integration**: Seamless integration with existing FastAPI structure
3. **Testing**: Comprehensive test coverage (>80%)
4. **Performance**: Parsing time <10 seconds per statement
5. **Reliability**: 95%+ transaction extraction accuracy

## Rollback Plan

If integration fails:
1. Keep existing parser as fallback
2. Add feature flag to disable GitHub parser
3. Document issues and create bug tickets
4. Revert to previous working state

## Timeline Estimate

- **Phase 1-2**: 2-3 hours (Installation & Adapter creation)
- **Phase 3-4**: 2-3 hours (Integration & Configuration)
- **Phase 5**: 4-6 hours (Testing)
- **Phase 6-7**: 1-2 hours (Error handling & Documentation)
- **Phase 8**: 1 hour (Migration setup)

**Total**: 10-15 hours

## Next Steps

1. Start with Phase 1: Install GitHub package
2. Create adapter module (Phase 2)
3. Test adapter with sample files (Phase 5)
4. Integrate with existing code (Phase 3-4)
5. Comprehensive testing (Phase 5)
6. Documentation (Phase 7)

