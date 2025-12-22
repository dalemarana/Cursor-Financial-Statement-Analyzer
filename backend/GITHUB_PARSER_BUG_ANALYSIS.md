# GitHub Parser Bug Analysis: KeyError: 'data'

## The Problem

The `KeyError: 'data'` error occurs in the GitHub parser's `parse_statement_accounts.py` file at line 353. This is **NOT a bug in our adapter code** - it's a bug in the GitHub parser itself.

## Root Cause Analysis

### Location of the Bug
File: `bank_statement_parser/parse_statement_accounts.py`
Line: 353
```python
cleaned_transactions = current_transaction["data"]
```

### Why It Happens

The bug occurs in the `parse_extract_clean()` function's while loop. Here's the problematic code flow:

```python
while(cleaned_transactions):
    try:
        if cleaned_transactions[1].capitalize() in MONTHS and is_integer(cleaned_transactions[0]):
            current_transaction = extract_transaction_date(cleaned_transactions)  # ✅ Sets current_transaction
            
        elif cleaned_transactions[0] in MONTHS and is_integer(cleaned_transactions[1]):
            current_transaction = extract_transaction_date(cleaned_transactions)  # ✅ Sets current_transaction
            
        elif cleaned_transactions[0] in paid_in or cleaned_transactions[0] in paid_out:
            current_transaction = {"data": cleaned_transactions, "transaction_date": current_date}  # ❌ BUG: current_date not initialized!
            
        elif cleaned_transactions[1] in paid_in or cleaned_transactions[1] in paid_out:
            cleaned_transactions.pop(0)
            current_transaction = {"data": cleaned_transactions, "transaction_date": current_date}  # ❌ BUG: current_date not initialized!
            
        else:
            cleaned_transactions.pop(0)
            cleaned_transactions = delete_items(cleaned_transactions)
            current_transaction = extract_transaction_date(cleaned_transactions)  # ⚠️ May raise ValueError
            
    except ValueError as ve:
        print(f"Value Error: {ve}. Deleting this line...")
        break  # ❌ Exits loop, but current_transaction might not be set
    except IndexError as e:
        pass  # ❌ BUG: If IndexError occurs, current_transaction is never set!
    
    # ❌ BUG: This line executes even if current_transaction was never set
    cleaned_transactions = current_transaction["data"]  # KeyError if current_transaction is empty dict or not set
    current_date = current_transaction["transaction_date"]
```

### Specific Issues

1. **Uninitialized Variable (Lines 332, 337)**
   - Uses `current_date` before it's initialized
   - `current_date` is only set on line 354, AFTER the first successful transaction
   - If the first transaction matches `paid_in`/`paid_out` patterns, `current_date` is undefined → `NameError` or uses undefined variable

2. **Exception Handling Bug (Line 349)**
   - If an `IndexError` occurs (e.g., `cleaned_transactions[1]` doesn't exist), the code just `pass`es
   - But then line 353 tries to access `current_transaction["data"]` even though `current_transaction` was never set
   - This causes `KeyError: 'data'`

3. **ValueError Handling (Line 346)**
   - If `extract_transaction_date()` raises a `ValueError` (e.g., date parsing fails), the code breaks
   - But if this happens before `current_transaction` is set, the next iteration will fail

4. **Missing Validation**
   - No check to ensure `current_transaction` has a "data" key before accessing it
   - No initialization of `current_transaction` to an empty dict or None

## When Does This Bug Trigger?

The bug triggers when:

1. **Statement format doesn't match expected patterns**
   - The parser expects specific date formats (e.g., "01 Nov" or "Nov 01")
   - If the statement has a different format, none of the date conditions match
   - Falls through to the `else` block or exception handlers

2. **IndexError scenarios**
   - If `cleaned_transactions` is empty or has fewer items than expected
   - Accessing `cleaned_transactions[0]` or `cleaned_transactions[1]` fails
   - Exception is caught but `current_transaction` is never set

3. **Date parsing failures**
   - If `datetime.strptime()` in `extract_transaction_date()` fails
   - Raises `ValueError`, loop breaks, but state is inconsistent

4. **First transaction is a payment type**
   - If the first item in `cleaned_transactions` is a payment type (CREDIT/DEBIT)
   - Tries to use `current_date` which hasn't been set yet

## Is Our Adapter Code Wrong?

**No, our adapter code is correct.** The issue is entirely within the GitHub parser. Our adapter:

1. ✅ Correctly calls `parse_bank_statement()` with proper parameters
2. ✅ Handles exceptions gracefully (catches and logs them)
3. ✅ Falls back to the new parser when GitHub parser fails
4. ✅ Converts the flat list format correctly (when it works)

## Evidence

Looking at our test results:
- **AMEX Credit Card**: Works with fallback parser (97.2% accuracy)
- **All other files**: GitHub parser fails with `KeyError: 'data'`
- **Fallback parser**: Successfully handles AMEX, partially handles others

This suggests:
- The GitHub parser has bugs that prevent it from parsing most statement formats
- Our fallback parser is working correctly
- The integration (adapter + fallback) is functioning as designed

## Potential Fixes (in GitHub Parser)

To fix this in the GitHub parser, you would need to:

1. **Initialize `current_date` before the loop**
   ```python
   current_date = None  # or some default
   ```

2. **Check if `current_transaction` is set before accessing it**
   ```python
   if "data" not in current_transaction:
       break  # or handle error
   cleaned_transactions = current_transaction["data"]
   ```

3. **Handle IndexError properly**
   ```python
   except IndexError as e:
       # Set current_transaction to empty or break
       break
   ```

4. **Validate data before processing**
   ```python
   if not cleaned_transactions or len(cleaned_transactions) < 2:
       break
   ```

## Conclusion

The `KeyError: 'data'` is **NOT caused by our adapter code**. It's a bug in the GitHub parser's error handling and state management. Our adapter correctly:

- Calls the GitHub parser with proper parameters
- Catches and handles exceptions
- Falls back to the working parser when GitHub parser fails

The fallback mechanism is working as designed, which is why we get good results for AMEX (97.2% accuracy) using the fallback parser.

