"""Transaction routes."""
from typing import List, Optional
import json
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import date
from decimal import Decimal
from uuid import UUID

from src.database.connection import get_db
from src.database.models import User, Transaction
from src.auth.middleware import get_current_active_user
from src.api.schemas import (
    TransactionResponse,
    TransactionCreate,
    TransactionUpdate,
    TransactionFilter
)

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


def build_transaction_query(
    db: Session,
    user_id: UUID,
    filters: Optional[TransactionFilter] = None
):
    """Build a query with filters applied."""
    query = db.query(Transaction).filter(Transaction.user_id == user_id)
    
    if not filters:
        return query
    
    # Date range filter
    if filters.date_range_start:
        query = query.filter(Transaction.date >= filters.date_range_start)
    if filters.date_range_end:
        query = query.filter(Transaction.date <= filters.date_range_end)
    
    # Category filter
    if filters.categories:
        query = query.filter(Transaction.category.in_(filters.categories))
    
    # Account filter
    if filters.accounts:
        query = query.filter(Transaction.account_name.in_(filters.accounts))
    
    # Amount range filter
    if filters.amount_min:
        query = query.filter(Transaction.amount >= filters.amount_min)
    if filters.amount_max:
        query = query.filter(Transaction.amount <= filters.amount_max)
    
    # Transaction type filter
    if filters.transaction_types:
        query = query.filter(Transaction.transaction_type.in_(filters.transaction_types))
    
    # Match status filter
    if filters.match_status:
        if filters.match_status == "matched":
            query = query.filter(Transaction.matched_transaction_id.isnot(None))
        elif filters.match_status == "unmatched":
            query = query.filter(Transaction.matched_transaction_id.is_(None))
        elif filters.match_status == "pending":
            query = query.filter(Transaction.is_confirmed == False)
    
    # Text search
    if filters.search_text:
        search_term = f"%{filters.search_text}%"
        query = query.filter(
            or_(
                Transaction.description.ilike(search_term),
                Transaction.account_name.ilike(search_term)
            )
        )
    
    # Vendor filter (searches in description)
    if filters.vendors:
        vendor_conditions = [
            Transaction.description.ilike(f"%{vendor}%") for vendor in filters.vendors
        ]
        query = query.filter(or_(*vendor_conditions))
    
    return query


@router.get("", response_model=List[TransactionResponse])
async def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    filters: Optional[str] = Query(None, description="JSON-encoded TransactionFilter"),
    search_text: Optional[str] = Query(None, description="Search text for description/account"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get transactions with optional filters."""
    # Parse filters from JSON string if provided
    filter_obj = None
    if filters:
        try:
            filter_dict = json.loads(filters)
            filter_obj = TransactionFilter(**filter_dict)
        except (json.JSONDecodeError, ValueError):
            # If JSON parsing fails, ignore filters
            pass
    
    # If search_text is provided as direct query param, use it
    if search_text and not filter_obj:
        filter_obj = TransactionFilter(search_text=search_text)
    elif search_text and filter_obj:
        filter_obj.search_text = search_text
    
    query = build_transaction_query(db, current_user.id, filter_obj)
    transactions = query.offset(skip).limit(limit).all()
    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a single transaction by ID."""
    transaction = db.query(Transaction).filter(
        and_(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        )
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: UUID,
    transaction_update: TransactionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a transaction."""
    transaction = db.query(Transaction).filter(
        and_(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        )
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Update fields
    if transaction_update.category is not None:
        transaction.category = transaction_update.category
    if transaction_update.subcategory is not None:
        transaction.subcategory = transaction_update.subcategory
    if transaction_update.account_name is not None:
        transaction.account_name = transaction_update.account_name
    if transaction_update.is_confirmed is not None:
        transaction.is_confirmed = transaction_update.is_confirmed
    
    db.commit()
    db.refresh(transaction)
    
    return transaction


@router.post("/bulk-update", response_model=List[TransactionResponse])
async def bulk_update_transactions(
    updates: List[dict],  # List of {transaction_id, category, subcategory, etc.}
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Bulk update multiple transactions."""
    updated_transactions = []
    
    for update in updates:
        transaction_id = UUID(update.get("transaction_id"))
        transaction = db.query(Transaction).filter(
            and_(
                Transaction.id == transaction_id,
                Transaction.user_id == current_user.id
            )
        ).first()
        
        if transaction:
            if "category" in update:
                transaction.category = update["category"]
            if "subcategory" in update:
                transaction.subcategory = update["subcategory"]
            if "account_name" in update:
                transaction.account_name = update["account_name"]
            if "is_confirmed" in update:
                transaction.is_confirmed = update["is_confirmed"]
            
            updated_transactions.append(transaction)
    
    db.commit()
    for transaction in updated_transactions:
        db.refresh(transaction)
    
    return updated_transactions


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a transaction."""
    transaction = db.query(Transaction).filter(
        and_(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        )
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    db.delete(transaction)
    db.commit()
    
    return None


@router.get("/stats/summary")
async def get_transaction_stats(
    filters: Optional[TransactionFilter] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get transaction statistics."""
    query = build_transaction_query(db, current_user.id, filters)
    transactions = query.all()
    
    total_count = len(transactions)
    total_income = sum(
        float(t.amount) for t in transactions
        if t.transaction_type == "Paid In"
    )
    total_expense = sum(
        float(t.amount) for t in transactions
        if t.transaction_type == "Paid Out"
    )
    matched_count = sum(1 for t in transactions if t.matched_transaction_id)
    
    return {
        "total_count": total_count,
        "total_income": total_income,
        "total_expense": total_expense,
        "net_amount": total_income - total_expense,
        "matched_count": matched_count,
        "unmatched_count": total_count - matched_count
    }

