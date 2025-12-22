"""Validation routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.database.models import User
from src.auth.middleware import get_current_active_user
from src.validation.trial_balance import TrialBalanceChecker

router = APIRouter(prefix="/api/validation", tags=["validation"])
balance_checker = TrialBalanceChecker()


@router.get("/trial-balance")
async def get_trial_balance(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get trial balance report."""
    report = balance_checker.validate_balance(db, str(current_user.id))
    
    return {
        "is_balanced": report.is_balanced,
        "trial_balance": {
            "assets": float(report.trial_balance.assets),
            "liabilities": float(report.trial_balance.liabilities),
            "equity": float(report.trial_balance.equity),
            "income": float(report.trial_balance.income),
            "expenses": float(report.trial_balance.expenses),
            "left_side": float(report.trial_balance.left_side),
            "right_side": float(report.trial_balance.right_side)
        },
        "discrepancy": float(report.discrepancy),
        "discrepancy_percentage": report.discrepancy_percentage,
        "suggestions": report.suggestions
    }

