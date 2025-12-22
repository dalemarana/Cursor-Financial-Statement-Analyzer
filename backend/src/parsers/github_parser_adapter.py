"""Adapter for GitHub bank statement parser.

This module provides an adapter layer between the working GitHub parser
(which returns a flat list format) and our Transaction model.
"""
import os
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from src.models.transaction import Transaction
from src.parsers.parsing_matrix import ParsingMatrixLoader

logger = logging.getLogger(__name__)

try:
    from bank_statement_parser.parse_statement_accounts import parse_bank_statement
    from bank_statement_parser.config import load_parsing_details
    GITHUB_PARSER_AVAILABLE = True
    GITHUB_CONFIG_AVAILABLE = True
except ImportError as e:
    logger.warning(f"GitHub parser not available: {e}")
    GITHUB_PARSER_AVAILABLE = False
    GITHUB_CONFIG_AVAILABLE = False
    parse_bank_statement = None
    load_parsing_details = None


class ParameterMapper:
    """Maps parameters from parsing matrix to GitHub parser format."""
    
    def __init__(self, matrix_loader: ParsingMatrixLoader):
        """Initialize parameter mapper.
        
        Args:
            matrix_loader: ParsingMatrixLoader instance for accessing patterns
        """
        self.matrix_loader = matrix_loader
    
    def get_github_parser_params(
        self,
        file_path: str,
        bank_account_name: Optional[str],
        bank_name: str,
        account_type: str
    ) -> Dict[str, Any]:
        """Extract parameters needed for GitHub parser from parsing matrix.
        
        Args:
            file_path: Path to the PDF file
            bank_account_name: Account name from parsing matrix
            bank_name: Bank name (HSBC, AMEX, NatWest, Barclays)
            account_type: 'credit_card' or 'debit_card'
            
        Returns:
            Dictionary with parameters for parse_bank_statement()
        """
        # Try to get patterns from GitHub parser's config first (most reliable)
        patterns = {}
        if bank_account_name and GITHUB_CONFIG_AVAILABLE:
            try:
                github_config = load_parsing_details()
                if bank_account_name in github_config:
                    patterns = github_config[bank_account_name]
                    logger.info(f"Using GitHub parser config for {bank_account_name}")
            except Exception as e:
                logger.warning(f"Failed to load GitHub parser config: {e}")
        
        # Fall back to our parsing matrix if GitHub config not available or doesn't have the bank
        if not patterns and bank_account_name:
            patterns = self.matrix_loader.get_patterns(bank_account_name)
            # Ensure patterns is a dict, not None
            if patterns is None:
                patterns = {}
        
        # Extract year from file path or use current year
        year = self._extract_year_from_path(file_path)
        if not year:
            year = datetime.now().year
        
        # Get date pattern, paid_in, paid_out from patterns
        date_pattern = patterns.get('DATE_PATTERN') if isinstance(patterns, dict) else None
        paid_in = patterns.get('PAID_IN', []) if isinstance(patterns, dict) else []
        paid_out = patterns.get('PAID_OUT', []) if isinstance(patterns, dict) else []
        
        # GitHub parser expects date_pattern as list or tuple: [num_components, format_string]
        # Convert list to tuple if needed (both work, but tuple is more explicit)
        if date_pattern:
            if isinstance(date_pattern, list) and len(date_pattern) == 2:
                # Convert list to tuple for consistency
                date_pattern = tuple(date_pattern)
            elif not isinstance(date_pattern, (tuple, list)):
                # Invalid format, use defaults
                logger.warning(f"date_pattern is not a list or tuple, using defaults. Got: {type(date_pattern)}")
                date_pattern = None
        
        # If patterns not found or invalid, use defaults based on bank and account type
        if not date_pattern or not paid_in or not paid_out:
            defaults = self._get_default_patterns(bank_name, account_type)
            date_pattern = date_pattern or defaults.get('DATE_PATTERN')
            paid_in = paid_in or defaults.get('PAID_IN', [])
            paid_out = paid_out or defaults.get('PAID_OUT', [])
        
        # GitHub parser expects bank name in format "BankName_Accounttype" (e.g., "HSBC_Debit_card")
        # Format is: "BankName_Accounttype" with lowercase 'c' in "card"
        # Normalize bank name to match parsing matrix format (e.g., "NatWest" -> "Natwest")
        bank_name_normalized = bank_name
        if bank_name == "NatWest":
            bank_name_normalized = "Natwest"  # Parsing matrix uses lowercase 'w'
        elif bank_name == "AMEX":
            bank_name_normalized = "AMEX"  # Already correct
        elif bank_name == "HSBC":
            bank_name_normalized = "HSBC"  # Already correct
        elif bank_name == "Barclays":
            bank_name_normalized = "Barclays"  # Already correct
        
        # If we have bank_account_name and it exists in GitHub config, use it directly
        if bank_account_name and GITHUB_CONFIG_AVAILABLE:
            try:
                github_config = load_parsing_details()
                if bank_account_name in github_config:
                    github_bank_name = bank_account_name
                else:
                    # Try to construct it: "debit_card" -> "Debit_card" (capitalize first word only)
                    account_type_parts = account_type.split('_')
                    if len(account_type_parts) == 2:
                        # "debit_card" -> "Debit_card" (not "Debit_Card")
                        account_type_formatted = account_type_parts[0].capitalize() + '_' + account_type_parts[1]
                    else:
                        account_type_formatted = account_type.replace('_', ' ').title().replace(' ', '_')
                    github_bank_name = f"{bank_name_normalized}_{account_type_formatted}"
            except Exception:
                # Fallback to construction
                account_type_parts = account_type.split('_')
                if len(account_type_parts) == 2:
                    account_type_formatted = account_type_parts[0].capitalize() + '_' + account_type_parts[1]
                else:
                    account_type_formatted = account_type.replace('_', ' ').title().replace(' ', '_')
                github_bank_name = f"{bank_name_normalized}_{account_type_formatted}"
        else:
            # Construct it manually
            account_type_parts = account_type.split('_')
            if len(account_type_parts) == 2:
                account_type_formatted = account_type_parts[0].capitalize() + '_' + account_type_parts[1]
            else:
                account_type_formatted = account_type.replace('_', ' ').title().replace(' ', '_')
            github_bank_name = f"{bank_name_normalized}_{account_type_formatted}"
        
        return {
            'bank': github_bank_name,
            'year': year,
            'date_pattern': date_pattern,
            'paid_in': paid_in if isinstance(paid_in, list) else [paid_in] if paid_in else [],
            'paid_out': paid_out if isinstance(paid_out, list) else [paid_out] if paid_out else [],
            'file': file_path,
            'folder': os.path.dirname(file_path),
            'test_mode': False
        }
    
    def _extract_year_from_path(self, file_path: str) -> Optional[int]:
        """Extract year from file path or filename.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Year as integer, or None if not found
        """
        # Try to extract year from filename
        filename = os.path.basename(file_path)
        
        # Look for 4-digit year pattern (20xx or 19xx)
        # Match years that appear with underscores, dashes, spaces, or at word boundaries
        import re
        # Pattern: (non-digit or start)(20xx or 19xx)(non-digit or end)
        year_match = re.search(r'(?:^|[^\d])(20\d{2}|19\d{2})(?:[^\d]|$)', filename)
        if year_match:
            return int(year_match.group(1))
        
        return None
    
    def _get_default_patterns(self, bank_name: str, account_type: str) -> Dict[str, Any]:
        """Get default patterns for bank and account type.
        
        Args:
            bank_name: Bank name
            account_type: 'credit_card' or 'debit_card'
            
        Returns:
            Dictionary with default patterns
        """
        defaults = {
            'HSBC': {
                'credit_card': {
                    'DATE_PATTERN': (2, "%d %b"),  # Tuple: (num_components, format_string)
                    'PAID_IN': ['PAID', 'IN'],
                    'PAID_OUT': ['PAID', 'OUT']
                },
                'debit_card': {
                    'DATE_PATTERN': (2, "%d %b"),  # Tuple: (num_components, format_string)
                    'PAID_IN': ['PAID', 'IN'],
                    'PAID_OUT': ['PAID', 'OUT']
                }
            },
            'AMEX': {
                'credit_card': {
                    'DATE_PATTERN': (2, "%d %b"),  # Tuple: (num_components, format_string)
                    'PAID_IN': ['CREDIT'],
                    'PAID_OUT': ['DEBIT']
                }
            },
            'Barclays': {
                'debit_card': {
                    'DATE_PATTERN': (2, "%d %b"),  # Tuple: (num_components, format_string)
                    'PAID_IN': ['CREDIT'],
                    'PAID_OUT': ['DEBIT']
                }
            },
            'NatWest': {
                'debit_card': {
                    'DATE_PATTERN': (2, "%d %b"),  # Tuple: (num_components, format_string)
                    'PAID_IN': ['CREDIT'],
                    'PAID_OUT': ['DEBIT']
                }
            }
        }
        
        return defaults.get(bank_name, {}).get(account_type, {})


class GitHubParserAdapter:
    """Adapter for GitHub bank statement parser.
    
    Converts the flat list format from parse_bank_statement() to
    our Transaction model format.
    """
    
    def __init__(self, matrix_loader: Optional[ParsingMatrixLoader] = None):
        """Initialize adapter.
        
        Args:
            matrix_loader: Optional ParsingMatrixLoader for parameter mapping
        """
        if not GITHUB_PARSER_AVAILABLE:
            raise ImportError(
                "GitHub parser not available. Install with: "
                "pip install git+https://github.com/dalemarana/bankStatementParser.git"
            )
        
        self.matrix_loader = matrix_loader or ParsingMatrixLoader()
        self.parameter_mapper = ParameterMapper(self.matrix_loader)
    
    def parse(
        self,
        file_path: str,
        bank_name: str,
        account_type: str,
        bank_account_name: Optional[str] = None
    ) -> List[Transaction]:
        """Parse bank statement using GitHub parser.
        
        Args:
            file_path: Path to the PDF file
            bank_name: Bank name (HSBC, AMEX, NatWest, Barclays)
            account_type: 'credit_card' or 'debit_card'
            bank_account_name: Optional account name from parsing matrix
            
        Returns:
            List of Transaction objects
            
        Raises:
            ImportError: If GitHub parser is not available
            FileNotFoundError: If file_path doesn't exist
            ValueError: If parsing fails
        """
        if not GITHUB_PARSER_AVAILABLE:
            raise ImportError("GitHub parser not available")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get parameters for GitHub parser
        params = self.parameter_mapper.get_github_parser_params(
            file_path=file_path,
            bank_account_name=bank_account_name,
            bank_name=bank_name,
            account_type=account_type
        )
        
        logger.info(f"Parsing {file_path} with GitHub parser (bank={bank_name}, type={account_type})")
        
        try:
            # Call GitHub parser
            flat_list = parse_bank_statement(
                bank=params['bank'],
                year=params['year'],
                date_pattern=params['date_pattern'],
                paid_in=params['paid_in'],
                paid_out=params['paid_out'],
                file=params['file'],
                folder=params['folder'],
                test_mode=params['test_mode']
            )
            
            logger.info(f"GitHub parser returned {len(flat_list)} items")
            
            # Convert flat list to Transaction objects
            transactions = self._convert_flat_list(flat_list)
            
            logger.info(f"Converted to {len(transactions)} transactions")
            
            return transactions
            
        except Exception as e:
            logger.error(f"GitHub parser failed: {e}", exc_info=True)
            raise ValueError(f"Failed to parse statement: {e}") from e
    
    def _convert_flat_list(self, flat_list: List[Any]) -> List[Transaction]:
        """Convert flat list format to Transaction objects.
        
        GitHub parser returns: [date1, type1, details1, amount1, date2, type2, ...]
        
        Args:
            flat_list: Flat list from GitHub parser
            
        Returns:
            List of Transaction objects
        """
        transactions = []
        
        # Process in groups of 4: [date, type, details, amount]
        i = 0
        while i < len(flat_list):
            try:
                # Extract date
                if i >= len(flat_list):
                    break
                date_obj = self._normalize_date(flat_list[i])
                if not date_obj:
                    i += 1
                    continue
                
                # Extract transaction type
                if i + 1 >= len(flat_list):
                    break
                transaction_type = self._normalize_transaction_type(flat_list[i + 1])
                
                # Extract description
                if i + 2 >= len(flat_list):
                    break
                description = self._normalize_description(flat_list[i + 2])
                
                # Extract amount
                if i + 3 >= len(flat_list):
                    break
                amount = self._normalize_amount(flat_list[i + 3])
                
                # Create Transaction object
                transaction = Transaction(
                    date=date_obj,
                    amount=amount,
                    description=description,
                    transaction_type=transaction_type
                )
                
                transactions.append(transaction)
                
                # Move to next group
                i += 4
                
            except (IndexError, ValueError, TypeError) as e:
                logger.warning(f"Error converting item at index {i}: {e}")
                # Try to skip to next potential date
                i += 1
        
        return transactions
    
    def _normalize_date(self, value: Any) -> Optional[date]:
        """Normalize date value to date object.
        
        Args:
            value: Date value (datetime, date, or string)
            
        Returns:
            date object, or None if invalid
        """
        # Check datetime first since datetime is a subclass of date
        if isinstance(value, datetime):
            return value.date()
        elif isinstance(value, date):
            return value
        elif isinstance(value, str):
            # Try to parse common date formats
            try:
                dt = datetime.strptime(value, "%Y-%m-%d")
                return dt.date()
            except ValueError:
                pass
            try:
                dt = datetime.strptime(value, "%d %b %Y")
                return dt.date()
            except ValueError:
                pass
        
        return None
    
    def _normalize_transaction_type(self, value: Any) -> str:
        """Normalize transaction type to 'Paid In' or 'Paid Out'.
        
        Args:
            value: Transaction type value
            
        Returns:
            'Paid In' or 'Paid Out'
        """
        if not value:
            return "Paid Out"
        
        value_str = str(value).upper()
        
        # Check for "Paid In" indicators
        if any(indicator in value_str for indicator in ['PAID IN', 'CREDIT', 'DEPOSIT', 'IN']):
            return "Paid In"
        
        # Check for "Paid Out" indicators
        if any(indicator in value_str for indicator in ['PAID OUT', 'DEBIT', 'WITHDRAWAL', 'OUT']):
            return "Paid Out"
        
        # Default to "Paid Out"
        return "Paid Out"
    
    def _normalize_description(self, value: Any) -> Optional[str]:
        """Normalize description value.
        
        Args:
            value: Description value
            
        Returns:
            Description string, or None if invalid
        """
        if not value:
            return None
        
        description = str(value).strip()
        
        # Remove empty descriptions
        if not description or description.lower() in ['none', 'null', '']:
            return None
        
        return description
    
    def _normalize_amount(self, value: Any) -> Decimal:
        """Normalize amount value to Decimal.
        
        Args:
            value: Amount value (float, int, string, or Decimal)
            
        Returns:
            Decimal amount
            
        Raises:
            ValueError: If value cannot be converted to Decimal
        """
        if isinstance(value, Decimal):
            return value
        elif isinstance(value, (int, float)):
            return Decimal(str(value))
        elif isinstance(value, str):
            # Remove currency symbols and commas
            cleaned = value.replace('£', '').replace('$', '').replace(',', '').strip()
            try:
                return Decimal(cleaned)
            except Exception as e:
                raise ValueError(f"Cannot convert {value} to Decimal: {e}") from e
        else:
            raise ValueError(f"Cannot convert {value} to Decimal")
