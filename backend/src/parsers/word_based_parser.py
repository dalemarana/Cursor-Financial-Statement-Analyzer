"""Word-based parser that follows the working implementation approach."""
import calendar
import re
from typing import List, Optional, Dict, Tuple
from datetime import datetime
from decimal import Decimal
from src.models.transaction import Transaction

# Month abbreviations
MONTHS = [calendar.month_abbr[month] for month in range(1, 13)]

# Money pattern
MONEY_PATTERN = r"\b\d{1,3}(?:,\d{3})*(?:\.\d{2})\b"

# Bank groups
ACCOUNT_GROUP_A = ["HSBC_Debit_card", "Barclays_Debit_card", "Natwest_Debit_card"]
ACCOUNT_GROUP_B = ["HSBC_Credit_card", "AMEX_Credit_card"]


class WordBasedParser:
    """Parser that processes statements word-by-word following the working implementation."""
    
    def __init__(self, bank_account_name: str, parsing_patterns: Dict, statement_year: int):
        """Initialize word-based parser.
        
        Args:
            bank_account_name: Bank account name like "HSBC_Debit_card"
            parsing_patterns: Dictionary with DATE_PATTERN, PAID_IN, PAID_OUT
            statement_year: Year to use for dates without year component
        """
        self.bank_account_name = bank_account_name
        self.parsing_patterns = parsing_patterns
        self.statement_year = statement_year
        
        date_pattern = parsing_patterns.get('DATE_PATTERN', [])
        if isinstance(date_pattern, tuple) and len(date_pattern) == 2:
            self.date_num_components, self.date_format = date_pattern
        else:
            self.date_num_components = 3
            self.date_format = '%d %b %y'
        
        self.paid_in = parsing_patterns.get('PAID_IN', [])
        self.paid_out = parsing_patterns.get('PAID_OUT', [])
    
    def parse(self, text: str) -> List[Transaction]:
        """Parse transactions from text using word-by-word approach."""
        # Extract transaction lines
        trigger, transaction_lines = self._extract_transactions(text)
        
        # Clean data (remove trigger word)
        cleaned_lines = self._clean_data(transaction_lines, trigger)
        
        # Join all lines and split into words
        all_words = " ".join(cleaned_lines).split(" ")
        
        # For credit cards, arrange dates
        if self.bank_account_name in ACCOUNT_GROUP_B:
            all_words = self._arrange_dates_on_list(all_words)
        
        # Process word-by-word
        transactions = self._parse_word_by_word(all_words)
        
        return transactions
    
    def _extract_transactions(self, text: str) -> Tuple[Optional[str], List[str]]:
        """Extract transaction lines using trigger words or patterns.
        
        Returns:
            Tuple of (trigger_word, list_of_transaction_lines)
        """
        transactions = []
        trigger = None
        extracting = False
        lines = text.split("\n")
        
        if self.bank_account_name in ACCOUNT_GROUP_A:
            # Debit cards: extract between trigger words
            start_queue, end_queue = self._get_trigger_words()
            
            for line in lines:
                line_upper = line.upper()
                line_stripped = line.strip()
                
                # Check for end trigger first (case-insensitive)
                # If we find an end trigger, stop extracting and break
                for end in end_queue:
                    if end.upper() in line_upper:
                        extracting = False
                        break
                
                # Check for start trigger (case-insensitive)
                # If we find a start trigger, start extracting from next line
                matched_start = None
                for start in start_queue:
                    if start.upper() in line_upper:
                        matched_start = start
                        extracting = True
                        trigger = start
                        # Don't include the trigger line itself, continue to next line
                        break
                
                # Only add line if extracting and it's not a trigger line
                if extracting and line_stripped and not matched_start:
                    transactions.append(line_stripped)
        
        elif self.bank_account_name in ACCOUNT_GROUP_B:
            # Credit cards: extract lines with two month occurrences
            for line in lines:
                if self._has_two_month_occurrences(line):
                    if self.bank_account_name == "AMEX_Credit_card":
                        # Exclude "Statement Period" line
                        if not bool(re.search(r"Statement Period", line, re.IGNORECASE)):
                            transactions.append(line.strip())
                    elif self.bank_account_name == "HSBC_Credit_card":
                        transactions.append(line.strip())
        
        return trigger, transactions
    
    def _get_trigger_words(self) -> Tuple[List[str], List[str]]:
        """Get start and end trigger words for debit card extraction."""
        start_queue = []
        end_queue = []
        
        if self.bank_account_name == "Barclays_Debit_card":
            for month in MONTHS:
                start_queue.append(f"{month} Start balance")
                end_queue.append(f"{month} End balance")
        
        elif self.bank_account_name == "HSBC_Debit_card":
            start_queue.append("BALANCEBROUGHTFORWARD")
            end_queue.append("BALANCECARRIEDFORWARD")
        
        elif self.bank_account_name == "Natwest_Debit_card":
            start_queue.append("BROUGHT FORWARD")
            end_queue.append("Interest (variable)")
        
        else:
            start_queue.append("Start balance")
            end_queue.append("End Balance")
        
        return start_queue, end_queue
    
    def _has_two_month_occurrences(self, line: str) -> bool:
        """Check if line has two month abbreviations (for credit cards).
        
        Case-insensitive matching to catch variations like "Nov", "NOV", "nov".
        """
        line_upper = line.upper()
        count = 0
        for month in MONTHS:
            # Case-insensitive matching
            pattern = re.compile(re.escape(month), re.IGNORECASE)
            occurrences = list(pattern.finditer(line))
            count += len(occurrences)
            if count >= 2:
                return True
        return False
    
    def _clean_data(self, transaction_lines: List[str], trigger: Optional[str]) -> List[str]:
        """Remove trigger word from transaction lines (case-insensitive)."""
        if trigger:
            trigger_upper = trigger.upper()
            return [line for line in transaction_lines if trigger_upper not in line.upper()]
        return transaction_lines
    
    def _arrange_dates_on_list(self, word_list: List[str]) -> List[str]:
        """Arrange dates for credit cards (split months joined with dates).
        
        Example: "Nov29" -> "Nov", "29"
        Example: "Nov29Nov29" -> "Nov", "29", "Nov", "29"
        This matches the working implementation's arrange_dates_on_list function.
        """
        new_list = []
        pattern = r'\d+(?:,\d+)*(?:\.\d+)?CR'
        
        for item in word_list:
            # Remove CR from payment values
            if re.match(pattern, item):
                item = item.rstrip("CR")
            
            # Split month from date - use case-insensitive matching
            # Pattern matches month abbreviation followed by digits
            month_pattern = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(\d+)'
            
            # Find all month+date combinations
            matches = list(re.finditer(month_pattern, item, re.IGNORECASE))
            
            if matches:
                last_end = 0
                for match in matches:
                    # Add text before this match
                    if match.start() > last_end:
                        part_before = item[last_end:match.start()]
                        if part_before:
                            new_list.append(part_before)
                    
                    # Split month and date
                    month_text = match.group(1)
                    date_text = match.group(2)
                    new_list.append(month_text)
                    new_list.append(date_text)
                    last_end = match.end()
                
                # Add any remaining text after the last match
                if last_end < len(item):
                    remaining = item[last_end:]
                    if remaining:
                        new_list.append(remaining)
            else:
                new_list.append(item)
        
        return new_list
    
    def _is_month(self, word: str) -> bool:
        """Check if word is a month abbreviation."""
        return word.capitalize() in MONTHS
    
    def _is_integer(self, word: str) -> bool:
        """Check if word is an integer."""
        try:
            int(word)
            return True
        except ValueError:
            return False
    
    def _is_money_value(self, word: str) -> bool:
        """Check if word matches money pattern."""
        return bool(re.match(MONEY_PATTERN, word))
    
    def _capitalize_months(self, word_list: List[str]) -> List[str]:
        """Capitalize month abbreviations (for Natwest)."""
        result = []
        for item in word_list:
            if item.capitalize() in MONTHS:
                result.append(item.capitalize())
            else:
                result.append(item)
        return result
    
    def _delete_items_until_date(self, word_list: List[str]) -> List[str]:
        """Delete items until we can parse a valid date.
        
        This matches the working implementation's delete_items() function.
        """
        while True:
            try:
                # Check if we have a month at position 3 (after removing some items)
                # This is the key check from working implementation
                if len(word_list) > 3 and self._is_month(word_list[3]):
                    word_list.pop(0)
                    word_list.pop(0)
                
                # Try to parse date
                date_str = " ".join(word_list[:self.date_num_components])
                date_obj = datetime.strptime(date_str, self.date_format)
                return word_list
            
            except (ValueError, TypeError, IndexError):
                if word_list:
                    word_list.pop(0)
                else:
                    return word_list
    
    def _extract_transaction_date(self, word_list: List[str]) -> Dict:
        """Extract transaction date from word list.
        
        This matches the working implementation's extract_transaction_date function.
        """
        # Make a copy to avoid modifying the original
        word_list = word_list.copy()
        
        # For credit cards, delete some initial items
        if self.bank_account_name in ACCOUNT_GROUP_B:
            if self.bank_account_name == "HSBC_Credit_card":
                # Delete first 3 items
                for _ in range(3):
                    if word_list:
                        word_list.pop(0)
            elif self.bank_account_name == "AMEX_Credit_card":
                # Delete 3rd and 4th items (indices 2 and 3)
                # Need to pop from higher index first
                if len(word_list) > 3:
                    word_list.pop(3)
                if len(word_list) > 2:
                    word_list.pop(2)
        
        # Capitalize months for Natwest
        if self.bank_account_name == "Natwest_Debit_card":
            word_list = self._capitalize_months(word_list)
        
        # Parse date
        date_str = " ".join(word_list[:self.date_num_components])
        try:
            date_obj = datetime.strptime(date_str, self.date_format)
        except ValueError:
            # If parsing fails, try with current year
            if self.date_num_components == 2:
                date_str_with_year = f"{date_str} {self.statement_year}"
                try:
                    date_obj = datetime.strptime(date_str_with_year, f"{self.date_format} %Y")
                except ValueError:
                    raise
        
        # Add year if not in format
        if self.bank_account_name in ["Barclays_Debit_card", "Natwest_Debit_card", "AMEX_Credit_card"]:
            date_obj = date_obj.replace(year=self.statement_year)
        
        # Remove date components from list
        word_list = word_list[self.date_num_components:]
        
        return {"data": word_list, "transaction_date": date_obj.date()}
    
    def _transaction_type_check(self, word: str) -> str:
        """Determine transaction type from keyword."""
        if self.bank_account_name in ACCOUNT_GROUP_A:
            if word in self.paid_in:
                return "Paid In"
            elif word in self.paid_out:
                return "Paid Out"
            else:
                return "Paid Out"  # Default
        else:  # ACCOUNT_GROUP_B
            if word in self.paid_in:
                return "Paid In"
            else:
                return "Paid Out"
    
    def _parse_payment_details(self, word_list: List[str]) -> Dict:
        """Parse transaction type, details, and amount from word list.
        
        This exactly matches the working implementation's parse_payment_details function.
        It modifies the list in place by removing processed items.
        Returns dict with transaction_type, details, and amount (no remaining_data).
        """
        details = []
        amount = None
        
        # Working implementation: iterate through all items, collect details, find amount
        for item in word_list:
            if self._is_money_value(item):
                # Remove amount from list and convert
                word_list.remove(item)
                amount = Decimal(item.replace(",", ""))
                break
            else:
                # Collect all non-money items as details
                details.append(item)
        
        # Remove extracted details from word_list (working implementation does this)
        for item in details:
            if item in word_list:
                word_list.remove(item)
        
        # Get transaction type from first detail (which is the transaction type keyword)
        transaction_type = self._transaction_type_check(details[0]) if details else "Paid Out"
        
        # Format details string
        if self.bank_account_name in ACCOUNT_GROUP_A:
            # Skip first detail (transaction type), join rest
            details_str = " ".join(details[1:])
        else:  # ACCOUNT_GROUP_B
            # Join all details
            details_str = " ".join(details)
            details_str = details_str.replace(")))", "")
        
        # Return transaction info (word_list is modified in place, so caller uses it directly)
        return {
            "transaction_type": transaction_type,
            "details": details_str.strip(),
            "amount": amount if amount is not None else Decimal("0")
        }
    
    def _parse_word_by_word(self, word_list: List[str]) -> List[Transaction]:
        """Parse transactions word-by-word following the working implementation exactly.
        
        This matches the working implementation's parse_extract_clean() function flow.
        """
        transactions = []
        current_date = None
        
        while word_list:
            try:
                current_transaction = {}
                
                # Check for date pattern: integer followed by month (capitalized check)
                if len(word_list) > 1:
                    if (self._is_integer(word_list[0]) and 
                        word_list[1].capitalize() in MONTHS):
                        current_transaction = self._extract_transaction_date(word_list)
                        
                # Check for AMEX pattern: month followed by integer
                elif len(word_list) > 1 and word_list[0] in MONTHS and self._is_integer(word_list[1]):
                    current_transaction = self._extract_transaction_date(word_list)
                
                # Check for transaction type keyword (when we already have a date)
                elif word_list[0] in self.paid_in or word_list[0] in self.paid_out:
                    current_transaction = {
                        "data": word_list,
                        "transaction_date": current_date
                    }
                
                # Check for Natwest pattern: second word is transaction type
                elif (len(word_list) > 1 and 
                      (word_list[1] in self.paid_in or word_list[1] in self.paid_out)):
                    word_list.pop(0)
                    current_transaction = {
                        "data": word_list,
                        "transaction_date": current_date
                    }
                
                else:
                    # Code to delete anything that is not expected in the table
                    word_list.pop(0)
                    word_list = self._delete_items_until_date(word_list)
                    if not word_list:
                        break
                    current_transaction = self._extract_transaction_date(word_list)
            
            # Exception handling matches working implementation (lines 346-350)
            except ValueError as ve:
                # Working implementation prints error message and breaks
                # Match working implementation's behavior: print error and break
                print(f"Value Error: {ve}. Deleting this line...")
                break
            except IndexError:
                # End of list - pass through (continues to line 397)
                # Working implementation continues on IndexError
                pass
            
            # Completing data extraction from cleaned transactions
            # This ALWAYS happens after try/except block, matching working implementation
            # (lines 352-354 in working code)
            word_list = current_transaction["data"]
            current_date = current_transaction["transaction_date"]
            
            # Check if we have enough data (line 356-357 in working code)
            if len(current_transaction["data"]) <= 3:
                break
            
            # Parse payment details (modifies current_transaction["data"] in place)
            # (line 358 in working code)
            current_transaction.update(self._parse_payment_details(current_transaction["data"]))
        
            # Create Transaction object and add to list
            # (lines 361-364 in working code add to transactions list)
            # Working implementation appends all parsed transactions without strict validation
            # Only check that we have a date and amount (amount can be 0 or negative)
            if (current_transaction.get("transaction_date") and 
                current_transaction.get("amount") is not None):
                txn = Transaction(
                    date=current_transaction["transaction_date"],
                    amount=abs(current_transaction["amount"]),
                    description=current_transaction["details"][:255] if current_transaction.get("details") else None,
                    transaction_type=current_transaction["transaction_type"]
                )
                transactions.append(txn)
            
            # Update word_list with remaining data (payment_details modified the list in place)
            # Since word_list was set to current_transaction["data"] above, and parse_payment_details
            # modified current_transaction["data"] in place, word_list now contains the remaining data
            # Loop continues naturally with the modified word_list
        
        return transactions

