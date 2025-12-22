"""Transaction data model."""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID


@dataclass
class Transaction:
    """Transaction data model."""
    date: date
    amount: Decimal
    description: Optional[str] = None
    transaction_type: str = "Paid Out"  # "Paid In" or "Paid Out"
    account_name: Optional[str] = None
    balance: Optional[Decimal] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    statement_id: Optional[UUID] = None
    matched_transaction_id: Optional[UUID] = None
    match_confidence: Optional[Decimal] = None
    is_confirmed: bool = False

