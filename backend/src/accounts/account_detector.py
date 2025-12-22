"""Account name detection from transaction descriptions."""
import re
from typing import Optional
from src.models.transaction import Transaction


class AccountDetector:
    """Detects account names from transaction descriptions."""
    
    # Common account patterns
    ACCOUNT_PATTERNS = {
        "checking": ["CHECKING", "CURRENT", "CURRENT ACCOUNT"],
        "savings": ["SAVINGS", "SAVER", "SAVINGS ACCOUNT"],
        "credit_card": ["CREDIT CARD", "CREDIT", "CARD"],
        "investment": ["INVESTMENT", "INVEST", "PORTFOLIO"],
        "loan": ["LOAN", "MORTGAGE", "BORROWING"]
    }
    
    # Common bank account keywords
    BANK_KEYWORDS = [
        "TRANSFER", "PAYMENT", "DEPOSIT", "WITHDRAWAL",
        "FROM", "TO", "ACCOUNT", "ACCT"
    ]
    
    def detect_account_name(self, transaction: Transaction) -> Optional[str]:
        """Detect account name from transaction description."""
        if not transaction.description:
            return None
        
        description_upper = transaction.description.upper()
        
        # Check for explicit account mentions
        for account_type, patterns in self.ACCOUNT_PATTERNS.items():
            for pattern in patterns:
                if pattern in description_upper:
                    # Try to extract the full account name
                    account_name = self._extract_account_from_description(
                        transaction.description,
                        pattern
                    )
                    if account_name:
                        return account_name
        
        # Check for transfer patterns (FROM/TO)
        if "FROM" in description_upper or "TO" in description_upper:
            account_name = self._extract_transfer_account(transaction.description)
            if account_name:
                return account_name
        
        # Default based on transaction type
        if transaction.transaction_type == "Paid In":
            return "Income Account"
        elif transaction.transaction_type == "Paid Out":
            return "Expense Account"
        
        return None
    
    def _extract_account_from_description(self, description: str, pattern: str) -> Optional[str]:
        """Extract account name from description containing pattern."""
        # Simple extraction - can be enhanced
        pattern_upper = pattern.upper()
        desc_upper = description.upper()
        
        idx = desc_upper.find(pattern_upper)
        if idx != -1:
            # Try to get surrounding text
            start = max(0, idx - 20)
            end = min(len(description), idx + len(pattern) + 20)
            extracted = description[start:end].strip()
            return extracted
        
        return None
    
    def _extract_transfer_account(self, description: str) -> Optional[str]:
        """Extract account name from transfer description."""
        # Look for patterns like "FROM Account Name" or "TO Account Name"
        patterns = [
            r"FROM\s+([A-Z][A-Z\s]+?)(?:\s+TO|\s+ACCOUNT|$)",
            r"TO\s+([A-Z][A-Z\s]+?)(?:\s+FROM|\s+ACCOUNT|$)",
            r"ACCOUNT\s+([A-Z][A-Z\s]+?)(?:\s+FROM|\s+TO|$)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description.upper())
            if match:
                account_name = match.group(1).strip()
                if len(account_name) > 2:  # Filter out very short matches
                    return account_name
        
        return None

