"""Parsing matrix loader for bank statement parsing patterns."""
import os
import pandas as pd
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import calendar


class ParsingMatrixLoader:
    """Loads and manages bank statement parsing patterns from CSV files."""
    
    COLUMNS = ['BANK', 'DATE_PATTERN', 'PAID_IN', 'PAID_OUT']
    MATRIX_FOLDER = "bank_account_dictionary"
    
    def __init__(self, matrix_folder: Optional[str] = None):
        """Initialize the parsing matrix loader.
        
        Args:
            matrix_folder: Path to the folder containing parsing matrix CSV files.
                          Defaults to 'bank_account_dictionary' in the backend directory.
        """
        if matrix_folder:
            self.matrix_folder = matrix_folder
        else:
            # Default to backend/bank_account_dictionary
            backend_dir = Path(__file__).parent.parent.parent
            self.matrix_folder = os.path.join(backend_dir, self.MATRIX_FOLDER)
        
        self._data: Optional[Dict[str, Dict]] = None
        self._load_matrix()
    
    def _load_matrix(self) -> None:
        """Load the latest parsing matrix CSV file."""
        if not os.path.exists(self.matrix_folder):
            os.makedirs(self.matrix_folder)
            self._data = {}
            return
        
        # Find all CSV files in the directory
        files = [
            os.path.join(self.matrix_folder, f)
            for f in os.listdir(self.matrix_folder)
            if os.path.isfile(os.path.join(self.matrix_folder, f)) and f.endswith('.csv')
        ]
        
        if not files:
            self._data = {}
            return
        
        # Get the latest file (by modification time)
        latest_file = max(files, key=os.path.getmtime)
        
        try:
            # Read the CSV file
            df = pd.read_csv(latest_file)
            
            # Validate columns
            if not all(col in df.columns for col in self.COLUMNS):
                raise ValueError(f"CSV file must contain columns: {self.COLUMNS}")
            
            # Create dictionary from CSV
            self._data = {}
            for index, row in df.iterrows():
                bank = str(row[self.COLUMNS[0]]).strip()
                if not bank:
                    continue
                
                # Parse DATE_PATTERN: format is "[num_components, 'format_string']"
                date_pattern_str = str(row[self.COLUMNS[1]]).strip() if pd.notna(row[self.COLUMNS[1]]) else ""
                date_pattern = self._parse_date_pattern(date_pattern_str)
                
                # Parse PAID_IN: format is "['keyword1', 'keyword2']"
                paid_in_str = str(row[self.COLUMNS[2]]).strip() if pd.notna(row[self.COLUMNS[2]]) else ""
                paid_in = self._parse_keyword_list(paid_in_str)
                
                # Parse PAID_OUT: format is "['keyword1', 'keyword2']"
                paid_out_str = str(row[self.COLUMNS[3]]).strip() if pd.notna(row[self.COLUMNS[3]]) else ""
                paid_out = self._parse_keyword_list(paid_out_str)
                
                self._data[bank] = {
                    'DATE_PATTERN': date_pattern,
                    'PAID_IN': paid_in,
                    'PAID_OUT': paid_out
                }
        except Exception as e:
            raise ValueError(f"Error loading parsing matrix from {latest_file}: {str(e)}")
    
    def _parse_date_pattern(self, pattern_str: str) -> Optional[Tuple[int, str]]:
        """Parse date pattern string into (num_components, format_string).
        
        Args:
            pattern_str: String like "[3, '%d %b %y']" or "[2, '%d %b']"
        
        Returns:
            Tuple of (number_of_components, format_string) or None if invalid
        """
        if not pattern_str or pattern_str == 'nan':
            return None
        
        try:
            # Remove whitespace and parse the list format
            pattern_str = pattern_str.strip()
            if pattern_str.startswith('[') and pattern_str.endswith(']'):
                # Use eval to parse the list (safe in this context as it's from our CSV)
                pattern_list = eval(pattern_str)
                if isinstance(pattern_list, list) and len(pattern_list) == 2:
                    num_components = int(pattern_list[0])
                    format_string = str(pattern_list[1])
                    return (num_components, format_string)
        except Exception:
            pass
        
        return None
    
    def _parse_keyword_list(self, keyword_str: str) -> List[str]:
        """Parse keyword list string into list of keywords.
        
        Args:
            keyword_str: String like "['CR', 'PAYMENT']" or "[]"
        
        Returns:
            List of keyword strings
        """
        if not keyword_str or keyword_str == 'nan' or keyword_str == '[]':
            return []
        
        try:
            keyword_str = keyword_str.strip()
            if keyword_str.startswith('[') and keyword_str.endswith(']'):
                # Use eval to parse the list (safe in this context as it's from our CSV)
                keyword_list = eval(keyword_str)
                if isinstance(keyword_list, list):
                    return [str(kw).strip() for kw in keyword_list if kw]
        except Exception:
            pass
        
        return []
    
    def get_patterns(self, bank_name: str) -> Optional[Dict]:
        """Get parsing patterns for a specific bank.
        
        Args:
            bank_name: Bank name in format like "HSBC_Credit_card" or "HSBC_Debit_card"
        
        Returns:
            Dictionary with DATE_PATTERN, PAID_IN, and PAID_OUT, or None if not found
        """
        if not self._data:
            return None
        
        return self._data.get(bank_name)
    
    def get_all_banks(self) -> List[str]:
        """Get list of all bank names in the parsing matrix.
        
        Returns:
            List of bank names
        """
        if not self._data:
            return []
        
        return list(self._data.keys())
    
    def reload(self) -> None:
        """Reload the parsing matrix from disk."""
        self._load_matrix()

