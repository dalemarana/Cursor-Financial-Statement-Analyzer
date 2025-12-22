"""Trial balance validation."""
from dataclasses import dataclass
from typing import List, Dict
from decimal import Decimal
from sqlalchemy.orm import Session
from src.database.models import Transaction


@dataclass
class TrialBalance:
    """Trial balance data."""
    assets: Decimal
    liabilities: Decimal
    equity: Decimal
    income: Decimal
    expenses: Decimal
    
    @property
    def left_side(self) -> Decimal:
        """Left side: Assets + Expenses."""
        return self.assets + self.expenses
    
    @property
    def right_side(self) -> Decimal:
        """Right side: Liabilities + Equity + Income."""
        return self.liabilities + self.equity + self.income
    
    @property
    def difference(self) -> Decimal:
        """Difference between left and right side."""
        return abs(self.left_side - self.right_side)
    
    @property
    def is_balanced(self) -> bool:
        """Check if trial balance is balanced."""
        return self.difference < Decimal("0.01")  # Allow small rounding differences


@dataclass
class BalanceReport:
    """Balance validation report."""
    trial_balance: TrialBalance
    is_balanced: bool
    discrepancy: Decimal
    discrepancy_percentage: float
    suggestions: List[str]


class TrialBalanceChecker:
    """Checks trial balance and generates reports."""
    
    def calculate_trial_balance(
        self,
        db: Session,
        user_id: str,
        transactions: List[Transaction] = None
    ) -> TrialBalance:
        """Calculate trial balance from transactions."""
        if transactions is None:
            transactions = db.query(Transaction).filter(
                Transaction.user_id == user_id
            ).all()
        
        assets = Decimal("0")
        liabilities = Decimal("0")
        equity = Decimal("0")
        income = Decimal("0")
        expenses = Decimal("0")
        
        for transaction in transactions:
            if not transaction.category:
                continue
            
            amount = Decimal(str(transaction.amount))
            
            if transaction.transaction_type == "Paid In":
                # Credits increase assets, income, equity, decrease liabilities
                if transaction.category == "Asset":
                    assets += amount
                elif transaction.category == "Income":
                    income += amount
                elif transaction.category == "Equity":
                    equity += amount
                elif transaction.category == "Liability":
                    liabilities -= amount
            else:  # Paid Out
                # Debits increase expenses, liabilities, decrease assets, equity
                if transaction.category == "Expense":
                    expenses += amount
                elif transaction.category == "Liability":
                    liabilities += amount
                elif transaction.category == "Asset":
                    assets -= amount
                elif transaction.category == "Equity":
                    equity -= amount
        
        return TrialBalance(
            assets=assets,
            liabilities=liabilities,
            equity=equity,
            income=income,
            expenses=expenses
        )
    
    def validate_balance(
        self,
        db: Session,
        user_id: str,
        transactions: List[Transaction] = None
    ) -> BalanceReport:
        """Validate trial balance and generate report."""
        trial_balance = self.calculate_trial_balance(db, user_id, transactions)
        
        is_balanced = trial_balance.is_balanced
        discrepancy = trial_balance.difference
        
        # Calculate percentage
        total = trial_balance.left_side + trial_balance.right_side
        if total > 0:
            discrepancy_percentage = float(discrepancy / total * 100)
        else:
            discrepancy_percentage = 0.0
        
        # Generate suggestions
        suggestions = self._generate_suggestions(
            db, user_id, trial_balance, discrepancy
        )
        
        return BalanceReport(
            trial_balance=trial_balance,
            is_balanced=is_balanced,
            discrepancy=discrepancy,
            discrepancy_percentage=discrepancy_percentage,
            suggestions=suggestions
        )
    
    def _generate_suggestions(
        self,
        db: Session,
        user_id: str,
        trial_balance: TrialBalance,
        discrepancy: Decimal
    ) -> List[str]:
        """Generate suggestions for fixing balance discrepancies."""
        suggestions = []
        
        if trial_balance.is_balanced:
            suggestions.append("Trial balance is balanced. No action needed.")
            return suggestions
        
        # Check for uncategorized transactions
        uncategorized_count = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.category.is_(None)
        ).count()
        
        if uncategorized_count > 0:
            suggestions.append(
                f"Found {uncategorized_count} uncategorized transactions. "
                "Categorizing these may help balance the accounts."
            )
        
        # Check for unmatched transactions
        unmatched_count = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.matched_transaction_id.is_(None)
        ).count()
        
        if unmatched_count > 0:
            suggestions.append(
                f"Found {unmatched_count} unmatched transactions. "
                "Matching these may help balance the accounts."
            )
        
        # Suggest which side needs adjustment
        if trial_balance.left_side > trial_balance.right_side:
            suggestions.append(
                f"Left side (Assets + Expenses) is higher by ${discrepancy:.2f}. "
                "Consider checking for missing income or liability entries."
            )
        else:
            suggestions.append(
                f"Right side (Liabilities + Equity + Income) is higher by ${discrepancy:.2f}. "
                "Consider checking for missing expense or asset entries."
            )
        
        return suggestions

