"""Statement upload and management routes."""
import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, date
import calendar

from src.database.connection import get_db
from src.database.models import User, Statement, Transaction
from src.auth.middleware import get_current_user
from src.api.schemas import StatementResponse
from src.parsers.pdf_parser import StatementParser
from src.accounts.account_detector import AccountDetector
from src.config import settings

router = APIRouter(prefix="/api/statements", tags=["statements"])
parser = StatementParser()
account_detector = AccountDetector()


@router.post("/upload", response_model=StatementResponse, status_code=status.HTTP_201_CREATED)
async def upload_statement(
    file: UploadFile = File(...),
    account_type: str = Form(..., description="Account type: 'credit_card' or 'debit_card'"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and parse a bank statement PDF.
    
    Args:
        file: PDF file to upload
        account_type: Either 'credit_card' or 'debit_card'
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )
    
    # Validate account type
    if account_type not in ['credit_card', 'debit_card']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="account_type must be 'credit_card' or 'debit_card'"
        )
    
    # Create upload directory if it doesn't exist
    upload_dir = os.path.join(settings.upload_dir, str(current_user.id))
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save file temporarily to extract statement period
    temp_file_path = os.path.join(upload_dir, file.filename)
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Detect bank type
    bank_name = parser.detect_bank(temp_file_path)
    if not bank_name:
        # Try to use filename or default
        bank_name = "Unknown"
    
    # Extract statement period (year, month_start, month_end)
    year, month_start, month_end = parser.extract_statement_period(temp_file_path)
    if not year:
        year = datetime.now().year
    if not month_start:
        month_start = datetime.now().month
    
    # Get month abbreviation
    month_abbr = calendar.month_abbr[month_start].upper()
    
    # Create new filename: {bank_name}_{month}_{year}.pdf
    # e.g., "HSBC_NOV_2024.pdf"
    new_filename = f"{bank_name}_{month_abbr}_{year}.pdf"
    new_file_path = os.path.join(upload_dir, new_filename)
    
    # Rename the file
    if temp_file_path != new_file_path:
        os.rename(temp_file_path, new_file_path)
    
    # Create bank_account_name for parsing matrix lookup
    # Format: "HSBC_Credit_card" or "HSBC_Debit_card" (capital first letter of account type)
    # The parsers expect exact format: "Debit_card" not "debit_card"
    # Normalize bank name to match parsing matrix format
    # Parsing matrix uses: "Natwest" not "NatWest", "HSBC" not "hsbc", etc.
    bank_name_normalized = bank_name
    if bank_name == "NatWest":
        bank_name_normalized = "Natwest"  # Parsing matrix uses lowercase 'w'
    elif bank_name == "AMEX":
        bank_name_normalized = "AMEX"  # Already correct
    elif bank_name == "HSBC":
        bank_name_normalized = "HSBC"  # Already correct
    elif bank_name == "Barclays":
        bank_name_normalized = "Barclays"  # Already correct
    
    account_type_parts = account_type.split('_')
    if len(account_type_parts) == 2:
        # "debit_card" -> "Debit_card" (not "debit_card")
        account_type_formatted = account_type_parts[0].capitalize() + '_' + account_type_parts[1]
    else:
        account_type_formatted = account_type.replace('_', ' ').title().replace(' ', '_')
    bank_account_name = f"{bank_name_normalized}_{account_type_formatted}"
    
    # Create statement record
    statement = Statement(
        user_id=current_user.id,
        file_name=new_filename,
        file_path=new_file_path,
        bank_name=bank_name,
        account_type=account_type,
        status="uploaded"
    )
    db.add(statement)
    db.commit()
    db.refresh(statement)
    
    # Parse transactions using parsing matrix
    try:
        transactions = parser.parse(
            new_file_path, 
            bank_account_name=bank_account_name, 
            bank_name=bank_name,
            account_type=account_type
        )
        
        # Save transactions to database
        for txn in transactions:
            # Detect account name
            account_name = account_detector.detect_account_name(txn)
            
            db_transaction = Transaction(
                user_id=current_user.id,
                statement_id=statement.id,
                date=txn.date,
                amount=txn.amount,
                description=txn.description,
                transaction_type=txn.transaction_type,
                account_name=account_name or txn.account_name,
                balance=txn.balance
            )
            db.add(db_transaction)
        
        statement.status = "parsed"
        statement.parsed_at = datetime.utcnow()
        db.commit()
        
    except Exception as e:
        statement.status = "error"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing statement: {str(e)}"
        )
    
    return statement


@router.get("", response_model=List[StatementResponse])
async def get_statements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all statements for the current user."""
    statements = db.query(Statement).filter(
        Statement.user_id == current_user.id
    ).order_by(Statement.uploaded_at.desc()).all()
    
    return statements


@router.get("/{statement_id}", response_model=StatementResponse)
async def get_statement(
    statement_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a single statement by ID."""
    statement = db.query(Statement).filter(
        Statement.id == statement_id,
        Statement.user_id == current_user.id
    ).first()
    
    if not statement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Statement not found"
        )
    
    return statement

