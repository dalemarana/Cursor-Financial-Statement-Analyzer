"""Transaction matching routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from src.database.connection import get_db
from src.database.models import User, Transaction
from src.auth.middleware import get_current_active_user
from src.matching.transaction_matcher import TransactionMatcher
from src.api.schemas import TransactionResponse

router = APIRouter(prefix="/api/matching", tags=["matching"])
matcher = TransactionMatcher(date_tolerance_days=2)


@router.post("/match")
async def match_transactions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Run matching algorithm on all user transactions."""
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.matched_transaction_id.is_(None)  # Only unmatched
    ).all()
    
    if len(transactions) < 2:
        return {
            "message": "Need at least 2 transactions to match",
            "matches_found": 0
        }
    
    # Convert to model format
    from src.models.transaction import Transaction as TransactionModel
    transaction_models = [
        TransactionModel(
            id=txn.id,
            date=txn.date,
            amount=txn.amount,
            description=txn.description,
            transaction_type=txn.transaction_type,
            account_name=txn.account_name,
            balance=txn.balance
        )
        for txn in transactions
    ]
    
    # Find matches
    matches = matcher.match_transactions(transaction_models)
    
    # Update database with matches
    match_count = 0
    for paid_out, paid_in, confidence in matches:
        # Find database transactions
        db_paid_out = db.query(Transaction).filter(Transaction.id == paid_out.id).first()
        db_paid_in = db.query(Transaction).filter(Transaction.id == paid_in.id).first()
        
        if db_paid_out and db_paid_in:
            db_paid_out.matched_transaction_id = db_paid_in.id
            db_paid_out.match_confidence = confidence
            db_paid_in.matched_transaction_id = db_paid_out.id
            db_paid_in.match_confidence = confidence
            match_count += 1
    
    db.commit()
    
    return {
        "message": f"Found {match_count} matches",
        "matches_found": match_count
    }


@router.get("/suggestions/{transaction_id}")
async def get_match_suggestions(
    transaction_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get match suggestions for a specific transaction."""
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Get all other transactions
    all_transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.id != transaction_id
    ).all()
    
    # Convert to model format
    from src.models.transaction import Transaction as TransactionModel
    transaction_model = TransactionModel(
        id=transaction.id,
        date=transaction.date,
        amount=transaction.amount,
        description=transaction.description,
        transaction_type=transaction.transaction_type,
        account_name=transaction.account_name
    )
    
    transaction_models = [
        TransactionModel(
            id=txn.id,
            date=txn.date,
            amount=txn.amount,
            description=txn.description,
            transaction_type=txn.transaction_type,
            account_name=txn.account_name
        )
        for txn in all_transactions
    ]
    
    # Get suggestions
    suggestions = matcher.find_potential_matches(transaction_model, transaction_models)
    
    return {
        "transaction_id": str(transaction_id),
        "suggestions": [
            {
                "transaction_id": str(sug.transaction2.id),
                "confidence": sug.confidence,
                "date_difference": sug.date_difference,
                "amount_match": sug.amount_match
            }
            for sug in suggestions[:10]  # Limit to top 10
        ]
    }


@router.get("/unmatched")
async def get_unmatched_transactions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all unmatched transactions."""
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.matched_transaction_id.is_(None)
    ).all()
    
    return [TransactionResponse.model_validate(txn) for txn in transactions]


@router.post("/confirm/{match_id}")
async def confirm_match(
    match_id: UUID,
    matched_with_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Confirm a match between two transactions."""
    transaction1 = db.query(Transaction).filter(
        Transaction.id == match_id,
        Transaction.user_id == current_user.id
    ).first()
    
    transaction2 = db.query(Transaction).filter(
        Transaction.id == matched_with_id,
        Transaction.user_id == current_user.id
    ).first()
    
    if not transaction1 or not transaction2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both transactions not found"
        )
    
    # Create match
    transaction1.matched_transaction_id = transaction2.id
    transaction2.matched_transaction_id = transaction1.id
    transaction1.is_confirmed = True
    transaction2.is_confirmed = True
    
    db.commit()
    
    return {
        "message": "Match confirmed",
        "transaction1_id": str(match_id),
        "transaction2_id": str(matched_with_id)
    }

