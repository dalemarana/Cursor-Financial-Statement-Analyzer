"""PDF bank statement parser."""
import pdfplumber
import re
import logging
from typing import List, Optional, Tuple, Dict
from datetime import datetime, date
from decimal import Decimal
from src.models.transaction import Transaction
from src.parsers.parsing_matrix import ParsingMatrixLoader
from src.parsers.word_based_parser import WordBasedParser
from src.config import settings

logger = logging.getLogger(__name__)


class PDFParser:
    """Base PDF parser class."""
    
    def parse(self, file_path: str) -> List[Transaction]:
        """Parse PDF and extract transactions."""
        raise NotImplementedError("Subclasses must implement parse method")
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from PDF."""
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    
    def extract_tables(self, file_path: str) -> List[List[List[str]]]:
        """Extract tables from PDF."""
        tables = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
        return tables


class GenericParser(PDFParser):
    """Generic parser that attempts to extract transactions from tables or text."""
    
    def __init__(self, parsing_patterns: Optional[Dict] = None, statement_year: Optional[int] = None):
        """Initialize parser with optional parsing patterns.
        
        Args:
            parsing_patterns: Dictionary with DATE_PATTERN, PAID_IN, PAID_OUT from parsing matrix
            statement_year: Year to use when parsing dates without year component
        """
        self.parsing_patterns = parsing_patterns
        self.statement_year = statement_year or datetime.now().year
    
    def parse(self, file_path: str) -> List[Transaction]:
        """Parse statement using generic table/text extraction."""
        transactions = []
        
        # Try extracting from tables first
        try:
            tables = self.extract_tables(file_path)
            transactions = self._parse_from_tables(tables)
            if transactions:
                return transactions
        except Exception:
            pass
        
        # Fallback to text parsing
        try:
            text = self.extract_text(file_path)
            transactions = self._parse_from_text(text)
        except Exception:
            pass
        
        return transactions
    
    def _parse_from_tables(self, tables: List[List[List[str]]]) -> List[Transaction]:
        """Parse transactions from extracted tables."""
        transactions = []
        
        for table in tables:
            if not table or len(table) < 2:
                continue
            
            # Try to find header row
            header_row_idx = None
            for idx, row in enumerate(table):
                if row and any(col and any(keyword in str(col).lower() for keyword in ['date', 'description', 'amount', 'balance', 'debit', 'credit']) for col in row):
                    header_row_idx = idx
                    break
            
            if header_row_idx is None:
                continue
            
            headers = [str(col).lower().strip() if col else '' for col in table[header_row_idx]]
            
            # Find column indices
            date_idx = self._find_column(headers, ['date', 'transaction date', 'value date'])
            desc_idx = self._find_column(headers, ['description', 'details', 'particulars', 'narration', 'transaction'])
            
            # Check for separate debit/credit columns
            debit_idx = self._find_column(headers, ['debit', 'withdrawal', 'paid out'])
            credit_idx = self._find_column(headers, ['credit', 'deposit', 'paid in'])
            amount_idx = self._find_column(headers, ['amount'])
            
            # Use debit/credit columns if available, otherwise use amount column
            if debit_idx is not None and credit_idx is not None:
                amount_idx = None  # Will use debit/credit columns instead
            elif debit_idx is not None:
                amount_idx = debit_idx
            elif credit_idx is not None:
                amount_idx = credit_idx
            
            balance_idx = self._find_column(headers, ['balance', 'running balance'])
            
            # Parse data rows
            for row in table[header_row_idx + 1:]:
                if not row or all(not col or str(col).strip() == '' for col in row):
                    continue
                
                try:
                    # Check if we have separate debit/credit columns
                    if debit_idx is not None and credit_idx is not None:
                        # Try debit first (if it has a value)
                        if debit_idx < len(row) and row[debit_idx] and str(row[debit_idx]).strip():
                            txn = self._parse_table_row(row, date_idx, desc_idx, debit_idx, balance_idx, "Paid Out")
                            if txn:
                                transactions.append(txn)
                        # Try credit (if it has a value)
                        if credit_idx < len(row) and row[credit_idx] and str(row[credit_idx]).strip():
                            txn = self._parse_table_row(row, date_idx, desc_idx, credit_idx, balance_idx, "Paid In")
                            if txn:
                                transactions.append(txn)
                    elif amount_idx is not None:
                        txn = self._parse_table_row(row, date_idx, desc_idx, amount_idx, balance_idx)
                        if txn:
                            transactions.append(txn)
                except Exception:
                    continue
        
        return transactions
    
    def _parse_from_text(self, text: str) -> List[Transaction]:
        """Parse transactions from plain text using regex patterns."""
        transactions = []
        
        # Skip if this looks like an AMEX statement (let AMEXParser handle it)
        if 'american express' in text.lower() or 'amex' in text.lower():
            return transactions
        
        # Common date patterns
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',  # DD/MM/YYYY or DD-MM-YYYY
            r'(\d{1,2}\s+\w{3}\s+\d{4})',  # DD MMM YYYY
        ]
        
        # Amount patterns - look for currency amounts with decimal places
        amount_pattern = r'([\d,]+\.\d{2})'  # More specific: requires decimal places
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line or len(line) < 10:
                continue
            
            # Skip summary/header lines
            if any(skip in line.lower() for skip in ['total', 'summary', 'statement period', 'credit limit', 'balance brought forward']):
                continue
            
            # Try to match date
            date_match = None
            for pattern in date_patterns:
                date_match = re.search(pattern, line)
                if date_match:
                    break
            
            if not date_match:
                continue
            
            # Try to extract amount (look for currency format)
            amounts = re.findall(amount_pattern, line)
            if not amounts:
                # Fallback to any number pattern
                amounts = re.findall(r'([\d,]+\.?\d*)', line)
            
            if not amounts:
                continue
            
            try:
                # Parse date
                date_str = date_match.group(1)
                date_obj = self._parse_date(date_str)
                if not date_obj:
                    continue
                
                # Parse amount (usually the last number in the line, or largest)
                amount_str = amounts[-1].replace(',', '')
                # Skip if amount looks like a date (e.g., 2024.00)
                if float(amount_str) > 10000:
                    continue
                
                amount = Decimal(amount_str)
                
                # Extract description (text between date and amount)
                desc_start = date_match.end()
                desc_end = line.rfind(amounts[-1])
                description = line[desc_start:desc_end].strip() if desc_end > desc_start else line[desc_start:].strip()
                
                # Skip if description is too short or looks like a header
                if len(description) < 3 or description.upper() == description and len(description) > 20:
                    continue
                
                # Determine transaction type using parsing matrix
                transaction_type = self._determine_transaction_type(description, None, amount)
                if amount < 0:
                    amount = abs(amount)
                
                # Clean description
                description = ' '.join(description.split())  # Remove extra whitespace
                description = description[:255] if description else None
                
                txn = Transaction(
                    date=date_obj,
                    amount=amount,
                    description=description,
                    transaction_type=transaction_type
                )
                transactions.append(txn)
            except (ValueError, Exception):
                continue
        
        return transactions
    
    def _find_column(self, headers: List[str], keywords: List[str]) -> Optional[int]:
        """Find column index by keywords."""
        for idx, header in enumerate(headers):
            if any(keyword in header for keyword in keywords):
                return idx
        return None
    
    def _parse_table_row(self, row: List[str], date_idx: Optional[int], 
                         desc_idx: Optional[int], amount_idx: Optional[int], 
                         balance_idx: Optional[int], 
                         transaction_type_override: Optional[str] = None) -> Optional[Transaction]:
        """Parse a single table row into a Transaction."""
        if date_idx is None or amount_idx is None:
            return None
        
        try:
            # Parse date
            date_str = str(row[date_idx]).strip() if date_idx < len(row) and row[date_idx] else None
            if not date_str:
                return None
            
            date_obj = self._parse_date(date_str)
            if not date_obj:
                return None
            
            # Parse amount
            amount_str = str(row[amount_idx]).strip() if amount_idx < len(row) and row[amount_idx] else None
            if not amount_str:
                return None
            
            # Clean amount string
            amount_str = re.sub(r'[^\d.-]', '', amount_str.replace(',', ''))
            if not amount_str:
                return None
            
            amount = Decimal(amount_str)
            
            # Parse description first (needed for transaction type determination)
            description = None
            if desc_idx is not None and desc_idx < len(row):
                description = str(row[desc_idx]).strip() if row[desc_idx] else None
            
            # Use override if provided, otherwise determine using parsing matrix
            if transaction_type_override:
                transaction_type = transaction_type_override
                amount = abs(amount)
            else:
                # Get transaction type column value if available
                txn_type_col = None
                # Try to find a transaction type column in the row
                # (This would need to be passed in, but for now we'll use description)
                transaction_type = self._determine_transaction_type(description or "", txn_type_col, amount)
                amount = abs(amount)
            
            # Parse balance
            balance = None
            if balance_idx is not None and balance_idx < len(row) and row[balance_idx]:
                try:
                    balance_str = str(row[balance_idx]).strip()
                    balance_str = re.sub(r'[^\d.-]', '', balance_str.replace(',', ''))
                    if balance_str:
                        balance = Decimal(balance_str)
                except Exception:
                    pass
            
            return Transaction(
                date=date_obj,
                amount=amount,
                description=description[:255] if description else None,
                transaction_type=transaction_type,
                balance=balance
            )
        except Exception:
            return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime.date]:
        """Parse date string into date object using parsing matrix patterns if available."""
        if not date_str:
            return None
        
        date_str = date_str.strip()
        
        # If we have parsing patterns, try those first
        if self.parsing_patterns and self.parsing_patterns.get('DATE_PATTERN'):
            date_pattern = self.parsing_patterns['DATE_PATTERN']
            if isinstance(date_pattern, tuple) and len(date_pattern) == 2:
                num_components, format_string = date_pattern
                parsed_date = self._parse_date_with_pattern(date_str, num_components, format_string)
                if parsed_date:
                    return parsed_date
        
        # Fallback to standard date formats
        formats = [
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%d/%m/%y',
            '%d-%m-%y',
            '%d %b %Y',
            '%d %B %Y',
            '%Y-%m-%d',
            '%d %b %y',  # e.g., "15 Jan 24"
            '%d %b',      # e.g., "15 Jan" (no year)
            '%b %d',      # e.g., "Jan 15" (no year)
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt).date()
                # If format doesn't include year, use statement year
                if '%y' not in fmt.lower() and '%Y' not in fmt:
                    try:
                        parsed = parsed.replace(year=self.statement_year)
                    except ValueError:
                        # Handle Feb 29 in non-leap years
                        parsed = parsed.replace(year=self.statement_year, day=28)
                return parsed
            except ValueError:
                continue
        
        # Try regex-based parsing
        match = re.match(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', date_str)
        if match:
            day, month, year = match.groups()
            year = int(year)
            if year < 100:
                year += 2000 if year < 50 else 1900
            try:
                return datetime(int(year), int(month), int(day)).date()
            except ValueError:
                pass
        
        return None
    
    def _parse_date_with_pattern(self, date_str: str, num_components: int, format_string: str) -> Optional[date]:
        """Parse date using the pattern from parsing matrix.
        
        Args:
            date_str: Date string to parse
            num_components: Number of date components (2 or 3)
            format_string: strptime format string
        
        Returns:
            Parsed date or None
        """
        try:
            # Split the date string into components
            parts = date_str.split()
            if len(parts) < num_components:
                return None
            
            # Take only the number of components specified
            date_part = ' '.join(parts[:num_components])
            
            # Parse with the format
            parsed = datetime.strptime(date_part, format_string)
            
            # If format doesn't include year, use statement year
            if num_components == 2:
                try:
                    parsed = parsed.replace(year=self.statement_year)
                except ValueError:
                    # Handle Feb 29 in non-leap years
                    parsed = parsed.replace(year=self.statement_year, day=28)
            
            return parsed.date()
        except (ValueError, IndexError):
            return None
    
    def _determine_transaction_type(self, description: Optional[str], 
                                   transaction_type_col: Optional[str] = None,
                                   amount: Optional[Decimal] = None) -> str:
        """Determine transaction type using parsing matrix keywords.
        
        Args:
            description: Transaction description
            transaction_type_col: Value from transaction type column (if available)
            amount: Transaction amount
        
        Returns:
            "Paid In" or "Paid Out"
        """
        # Check parsing matrix keywords first
        if self.parsing_patterns:
            paid_in_keywords = self.parsing_patterns.get('PAID_IN', [])
            paid_out_keywords = self.parsing_patterns.get('PAID_OUT', [])
            
            # Check in description
            if description:
                desc_upper = description.upper()
                for keyword in paid_in_keywords:
                    if keyword.upper() in desc_upper:
                        return "Paid In"
                for keyword in paid_out_keywords:
                    if keyword.upper() in desc_upper:
                        return "Paid Out"
            
            # Check in transaction type column
            if transaction_type_col:
                col_upper = transaction_type_col.upper()
                for keyword in paid_in_keywords:
                    if keyword.upper() in col_upper:
                        return "Paid In"
                for keyword in paid_out_keywords:
                    if keyword.upper() in col_upper:
                        return "Paid Out"
        
        # Fallback to default logic
        if description:
            desc_upper = description.upper()
            if any(keyword in desc_upper for keyword in ['PAYMENT', 'REFUND', 'CREDIT', 'DEPOSIT', 'RECEIVED']):
                return "Paid In"
        
        if amount and amount < 0:
            return "Paid Out"
        
        # Default to Paid Out for purchases
        return "Paid Out"


class HSBCParser(GenericParser):
    """HSBC bank statement parser."""
    
    def __init__(self, parsing_patterns: Optional[Dict] = None, statement_year: Optional[int] = None):
        """Initialize HSBC parser."""
        super().__init__(parsing_patterns, statement_year)
    
    def parse(self, file_path: str, bank_account_name: Optional[str] = None) -> List[Transaction]:
        """Parse HSBC statement."""
        # Try word-based parser first (matches working implementation)
        if bank_account_name and self.parsing_patterns:
            try:
                text = self.extract_text(file_path)
                word_parser = WordBasedParser(
                    bank_account_name=bank_account_name,
                    parsing_patterns=self.parsing_patterns,
                    statement_year=self.statement_year
                )
                transactions = word_parser.parse(text)
                if transactions:
                    return transactions
            except Exception:
                pass
        
        # Fallback to generic parser
        transactions = super().parse(file_path)
        return transactions
    
    def _parse_hsbc_text(self, text: str) -> List[Transaction]:
        """Parse HSBC-specific text format.
        
        HSBC format:
        Date Payment type and details Paidout Paidin Balance
        12 Nov 23 BALANCEBROUGHTFORWARD . 2,443.09
        13 Nov 23 CR UY C
        CELESTE TY GIRLY 6.00 2,449.09
        17 Nov 23 CR ICH NHS TRUST 119.17
        OBP AMERICAN EXP 3773
        PB9907******37285 38.98 2,529.28
        """
        transactions = []
        
        if not self.parsing_patterns or not self.parsing_patterns.get('DATE_PATTERN'):
            return transactions
        
        date_pattern_info = self.parsing_patterns['DATE_PATTERN']
        if not isinstance(date_pattern_info, tuple) or len(date_pattern_info) != 2:
            return transactions
        
        num_components, format_string = date_pattern_info
        paid_in_keywords = self.parsing_patterns.get('PAID_IN', [])
        paid_out_keywords = self.parsing_patterns.get('PAID_OUT', [])
        
        lines = text.split('\n')
        i = 0
        
        # Find the transaction table header
        header_found = False
        while i < len(lines):
            line = lines[i].strip()
            if 'Date' in line and ('Payment' in line or 'Paidout' in line or 'Paidin' in line):
                header_found = True
                i += 1
                break
            i += 1
        
        if not header_found:
            return transactions
        
        # Parse transactions
        current_date = None
        current_description_parts = []
        current_amount = None
        current_balance = None
        current_type = None
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                i += 1
                continue
            
            # Skip summary/header lines
            if any(skip in line.upper() for skip in ['ACCOUNT SUMMARY', 'OPENINGBALANCE', 'CLOSINGBALANCE', 
                                                      'PAYMENTS IN', 'PAYMENTS OUT', 'INTERNATIONAL BANK']):
                i += 1
                continue
            
            # Try to match date pattern at the start of the line
            # Pattern: "12 Nov 23" or "13 Nov 23"
            date_match = None
            if num_components == 3:
                # Try format like "12 Nov 23"
                date_match = re.match(r'^(\d{1,2})\s+(\w{3})\s+(\d{2})', line)
            elif num_components == 2:
                # Try format like "12 Nov"
                date_match = re.match(r'^(\d{1,2})\s+(\w{3})', line)
            
            if date_match:
                # Save previous transaction if we have one
                if current_date and current_amount is not None:
                    description = ' '.join(current_description_parts).strip()
                    if description and len(description) > 2:
                        transaction_type = current_type or self._determine_transaction_type(description, None, current_amount)
                        txn = Transaction(
                            date=current_date,
                            amount=abs(current_amount),
                            description=description[:255],
                            transaction_type=transaction_type,
                            balance=current_balance
                        )
                        transactions.append(txn)
                
                # Parse new date
                try:
                    if num_components == 3:
                        day, month_str, year_str = date_match.groups()
                        year = int(year_str)
                        if year < 50:
                            year += 2000
                        else:
                            year += 1900
                    else:
                        day, month_str = date_match.groups()
                        year = self.statement_year
                    
                    months = {
                        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
                    }
                    month = months.get(month_str.lower())
                    if month:
                        current_date = datetime(year, month, int(day)).date()
                    else:
                        current_date = None
                except (ValueError, KeyError):
                    current_date = None
                
                # Reset for new transaction
                current_description_parts = []
                current_amount = None
                current_balance = None
                current_type = None
                
                # Extract remaining parts of the line
                remaining = line[date_match.end():].strip()
                
                # Check for transaction type keywords
                remaining_upper = remaining.upper()
                if any(kw in remaining_upper for kw in paid_in_keywords):
                    current_type = "Paid In"
                elif any(kw in remaining_upper for kw in paid_out_keywords):
                    current_type = "Paid Out"
                
                # Try to extract amount and balance
                # Look for patterns like "6.00 2,449.09" or "38.98 2,529.28"
                amount_pattern = r'([\d,]+\.\d{2})'
                amounts = re.findall(amount_pattern, remaining)
                
                if len(amounts) >= 1:
                    # First amount is usually the transaction amount
                    current_amount = Decimal(amounts[0].replace(',', ''))
                    if len(amounts) >= 2:
                        # Second amount is usually the balance
                        current_balance = Decimal(amounts[1].replace(',', ''))
                
                # Extract description (text before amounts)
                if amounts:
                    desc_end = remaining.find(amounts[0])
                    description_part = remaining[:desc_end].strip()
                else:
                    description_part = remaining
                
                # Clean description
                description_part = re.sub(r'^\s*[CR|ATM|VIS|DD|OBP|BP|SO|TFR]\s+', '', description_part, flags=re.IGNORECASE)
                if description_part:
                    current_description_parts.append(description_part)
                
            elif current_date:
                # Continuation line - add to description
                # Check if this line contains an amount (might be the transaction line)
                amount_pattern = r'([\d,]+\.\d{2})'
                amounts = re.findall(amount_pattern, line)
                
                if amounts:
                    # This line has an amount, so it's likely the transaction amount line
                    if current_amount is None:
                        current_amount = Decimal(amounts[0].replace(',', ''))
                    if len(amounts) >= 2 and current_balance is None:
                        current_balance = Decimal(amounts[1].replace(',', ''))
                    
                    # Description is before the amount
                    desc_end = line.find(amounts[0])
                    description_part = line[:desc_end].strip()
                    if description_part:
                        current_description_parts.append(description_part)
                else:
                    # Just description continuation
                    line_clean = line.strip()
                    if line_clean and not line_clean.startswith('.'):
                        current_description_parts.append(line_clean)
            
            i += 1
        
        # Save last transaction
        if current_date and current_amount is not None:
            description = ' '.join(current_description_parts).strip()
            if description and len(description) > 2:
                transaction_type = current_type or self._determine_transaction_type(description, None, current_amount)
                txn = Transaction(
                    date=current_date,
                    amount=abs(current_amount),
                    description=description[:255],
                    transaction_type=transaction_type,
                    balance=current_balance
                )
                transactions.append(txn)
        
        return transactions


class AMEXParser(GenericParser):
    """AMEX credit card statement parser."""
    
    def __init__(self, parsing_patterns: Optional[Dict] = None, statement_year: Optional[int] = None):
        """Initialize AMEX parser."""
        super().__init__(parsing_patterns, statement_year)
    
    def parse(self, file_path: str, bank_account_name: Optional[str] = None) -> List[Transaction]:
        """Parse AMEX statement."""
        # Try word-based parser first (matches working implementation)
        if bank_account_name and self.parsing_patterns:
            try:
                text = self.extract_text(file_path)
                word_parser = WordBasedParser(
                    bank_account_name=bank_account_name,
                    parsing_patterns=self.parsing_patterns,
                    statement_year=self.statement_year
                )
                transactions = word_parser.parse(text)
                if transactions:
                    return transactions
            except Exception:
                pass
        
        # Fallback to original AMEX text parser
        text = self.extract_text(file_path)
        transactions = self._parse_amex_text(text)
        
        # If text parsing didn't work, fall back to generic parser
        if not transactions:
            transactions = super().parse(file_path)
        
        return transactions
    
    def _parse_amex_text(self, text: str) -> List[Transaction]:
        """Parse AMEX-specific text format.
        
        AMEX format examples:
        - "Nov29 Nov29 PAYMENT RECEIVED - THANK YOU 860.34"
        - "Nov7 Nov8 TFL TRAVEL CHARGE TFL.GOV.UK/CP 5.10"
        - "Nov7 Nov7 LIDL LONDON 1740 LONDON 8.39"
        """
        transactions = []
        
        # Month abbreviations
        months = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        lines = text.split('\n')
        current_year = 2024  # Default, will try to detect from statement
        
        # Try to detect year from statement period
        for line in lines[:100]:  # Check first 100 lines
            if 'statement period' in line.lower() or ('from' in line.lower() and 'to' in line.lower()):
                # Look for year in format like "2024"
                year_match = re.search(r'20\d{2}', line)
                if year_match:
                    current_year = int(year_match.group(0))
                    break
        
        # Pattern to match: "Nov29 Nov29 DESCRIPTION AMOUNT" or "Nov7 Nov8 DESCRIPTION AMOUNT"
        # Format: MonthDay MonthDay Description Amount
        # The amount is always at the end, may have CR/DR indicator
        pattern = r'^([A-Za-z]{3})(\d{1,2})\s+([A-Za-z]{3})(\d{1,2})\s+(.+?)\s+([\d,]+\.?\d{2})\s*(CR|DR)?$'
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 15:  # Minimum length for a valid transaction
                continue
            
            # Skip summary lines
            if any(skip in line.lower() for skip in ['total', 'summary', 'statement period', 'credit limit', 'minimum repayment']):
                continue
            
            match = re.match(pattern, line)
            
            if match:
                try:
                    month1_str, day1_str, _month2_str, _day2_str, description, amount_str, cr_dr = match.groups()
                    
                    # Use first date (transaction date)
                    month_str = month1_str.lower()
                    day = int(day1_str)
                    
                    # Get month number
                    month = months.get(month_str)
                    if not month:
                        continue
                    
                    # Parse date
                    try:
                        date_obj = datetime(current_year, month, day).date()
                    except ValueError:
                        # Handle invalid dates
                        continue
                    
                    # Parse amount
                    amount_str = amount_str.replace(',', '')
                    amount = Decimal(amount_str)
                    
                    # Clean description
                    description = description.strip()
                    # Remove extra whitespace
                    description = ' '.join(description.split())
                    # Limit length
                    description = description[:255] if description else None
                    
                    # Determine transaction type using parsing matrix or default logic
                    if cr_dr and cr_dr.upper() == 'CR':
                        transaction_type = "Paid In"
                    else:
                        transaction_type = self._determine_transaction_type(description, None, amount)
                    
                    txn = Transaction(
                        date=date_obj,
                        amount=amount,
                        description=description,
                        transaction_type=transaction_type
                    )
                    transactions.append(txn)
                except (ValueError, IndexError, AttributeError, TypeError) as e:
                    # Skip lines that don't match expected format
                    continue
        
        return transactions


class NatWestParser(GenericParser):
    """NatWest bank statement parser."""
    
    def __init__(self, parsing_patterns: Optional[Dict] = None, statement_year: Optional[int] = None):
        """Initialize NatWest parser."""
        super().__init__(parsing_patterns, statement_year)
    
    def parse(self, file_path: str, bank_account_name: Optional[str] = None) -> List[Transaction]:
        """Parse NatWest statement."""
        # Try word-based parser first (matches working implementation)
        if bank_account_name and self.parsing_patterns:
            try:
                text = self.extract_text(file_path)
                word_parser = WordBasedParser(
                    bank_account_name=bank_account_name,
                    parsing_patterns=self.parsing_patterns,
                    statement_year=self.statement_year
                )
                transactions = word_parser.parse(text)
                if transactions:
                    return transactions
            except Exception:
                pass
        
        # Fallback to generic parser
        transactions = super().parse(file_path)
        return transactions


class BarclaysParser(GenericParser):
    """Barclays bank statement parser."""
    
    def __init__(self, parsing_patterns: Optional[Dict] = None, statement_year: Optional[int] = None):
        """Initialize Barclays parser."""
        super().__init__(parsing_patterns, statement_year)
    
    def parse(self, file_path: str, bank_account_name: Optional[str] = None) -> List[Transaction]:
        """Parse Barclays statement."""
        # Try word-based parser first (matches working implementation)
        if bank_account_name and self.parsing_patterns:
            try:
                text = self.extract_text(file_path)
                word_parser = WordBasedParser(
                    bank_account_name=bank_account_name,
                    parsing_patterns=self.parsing_patterns,
                    statement_year=self.statement_year
                )
                transactions = word_parser.parse(text)
                if transactions:
                    return transactions
            except Exception:
                pass
        
        # Fallback to generic parser
        transactions = super().parse(file_path)
        return transactions


class StatementParser:
    """Main statement parser that detects bank type and uses appropriate parser."""
    
    def __init__(self, use_github_parser: Optional[bool] = None):
        """Initialize statement parser.
        
        Args:
            use_github_parser: Whether to use GitHub parser. If None, uses settings.use_github_parser
        """
        self.matrix_loader = ParsingMatrixLoader()
        self.parsers = {
            "HSBC": HSBCParser,
            "AMEX": AMEXParser,
            "NatWest": NatWestParser,
            "Barclays": BarclaysParser
        }
        
        # Determine whether to use GitHub parser
        self.use_github_parser = use_github_parser if use_github_parser is not None else settings.use_github_parser
        
        # Initialize GitHub adapter if needed
        self.github_adapter = None
        if self.use_github_parser:
            try:
                from src.parsers.github_parser_adapter import GitHubParserAdapter
                self.github_adapter = GitHubParserAdapter(matrix_loader=self.matrix_loader)
                logger.info("GitHub parser adapter initialized")
            except ImportError as e:
                logger.warning(f"GitHub parser adapter not available: {e}")
                self.use_github_parser = False
    
    def detect_bank(self, file_path: str) -> Optional[str]:
        """Detect bank type from PDF content."""
        parser = PDFParser()
        text = parser.extract_text(file_path).upper()
        
        if "HSBC" in text:
            return "HSBC"
        elif "AMERICAN EXPRESS" in text or "AMEX" in text:
            return "AMEX"
        elif "NATWEST" in text:
            return "NatWest"
        elif "BARCLAYS" in text:
            return "Barclays"
        
        return None
    
    def extract_statement_period(self, file_path: str) -> Tuple[Optional[int], Optional[int], Optional[int]]:
        """Extract statement period (year, month_start, month_end) from PDF.
        
        Returns:
            Tuple of (year, start_month, end_month) or (None, None, None) if not found
        """
        parser = PDFParser()
        text = parser.extract_text(file_path)
        
        # Look for statement period patterns
        # Common patterns: "Statement Period: 01 Nov 2024 - 30 Nov 2024"
        # or "From: 01/11/2024 To: 30/11/2024"
        patterns = [
            r'statement\s+period[:\s]+(\d{1,2})[-\s]+(\d{1,2})\s+(\w{3})\s+(\d{4})',
            r'from[:\s]+(\d{1,2})[/-](\d{1,2})[/-](\d{4})[^\d]+to[:\s]+(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
            r'(\d{1,2})\s+(\w{3})\s+(\d{4})[^\d]+(\d{1,2})\s+(\w{3})\s+(\d{4})',
        ]
        
        months = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) >= 3:
                    # Try to extract year
                    year = None
                    for group in groups:
                        if group and len(str(group)) == 4 and str(group).isdigit():
                            year = int(group)
                            break
                    
                    if year:
                        # Try to extract month
                        month = None
                        for group in groups:
                            if isinstance(group, str) and group.lower() in months:
                                month = months[group.lower()]
                                break
                        
                        return (year, month, month)  # Return same month for start/end
        
        # Fallback: look for any year in the first few lines
        lines = text.split('\n')[:50]
        for line in lines:
            year_match = re.search(r'20\d{2}', line)
            if year_match:
                year = int(year_match.group(0))
                return (year, None, None)
        
        return (None, None, None)
    
    def parse(self, file_path: str, bank_account_name: Optional[str] = None, 
              bank_name: Optional[str] = None, account_type: Optional[str] = None) -> List[Transaction]:
        """Parse bank statement using parsing matrix.
        
        Args:
            file_path: Path to PDF file
            bank_account_name: Full bank account name like "HSBC_Credit_card" or "HSBC_Debit_card"
            bank_name: Simple bank name like "HSBC" (for backward compatibility)
            account_type: 'credit_card' or 'debit_card' (required for GitHub parser)
        
        Returns:
            List of Transaction objects
        """
        # Try GitHub parser first if enabled
        if self.use_github_parser and self.github_adapter:
            # Detect bank if not provided
            if not bank_name:
                bank_name = self.detect_bank(file_path)
            
            # Determine account type if not provided
            if not account_type and bank_account_name:
                if 'credit' in bank_account_name.lower():
                    account_type = 'credit_card'
                elif 'debit' in bank_account_name.lower():
                    account_type = 'debit_card'
            
            if bank_name and account_type:
                try:
                    logger.info(f"Attempting to parse with GitHub parser: {file_path}")
                    transactions = self.github_adapter.parse(
                        file_path=file_path,
                        bank_name=bank_name,
                        account_type=account_type,
                        bank_account_name=bank_account_name
                    )
                    if transactions:
                        logger.info(f"GitHub parser extracted {len(transactions)} transactions")
                        return transactions
                    else:
                        logger.warning("GitHub parser returned no transactions")
                except Exception as e:
                    logger.warning(f"GitHub parser failed: {e}")
                    if not settings.github_parser_fallback:
                        raise
                    # Fall through to use new parser
        
        # Fall back to new parser implementation
        logger.info(f"Using new parser implementation: {file_path}")
        
        # Get parsing patterns from matrix
        parsing_patterns = None
        if bank_account_name:
            parsing_patterns = self.matrix_loader.get_patterns(bank_account_name)
        
        # Extract statement period to get year
        year, month_start, month_end = self.extract_statement_period(file_path)
        if not year:
            year = datetime.now().year
        
        # Detect bank if not provided
        if not bank_name:
            bank_name = self.detect_bank(file_path)
        
        # Use specific parser if detected, otherwise use generic parser
        if bank_name and bank_name in self.parsers:
            parser_class = self.parsers[bank_name]
            parser = parser_class(parsing_patterns=parsing_patterns, statement_year=year)
            # Pass bank_account_name to parser if it supports it
            if hasattr(parser, 'parse') and bank_account_name:
                try:
                    return parser.parse(file_path, bank_account_name=bank_account_name)
                except TypeError:
                    # Parser doesn't accept bank_account_name parameter
                    return parser.parse(file_path)
            else:
                return parser.parse(file_path)
        else:
            # Use generic parser as fallback
            parser = GenericParser(parsing_patterns=parsing_patterns, statement_year=year)
            return parser.parse(file_path)

