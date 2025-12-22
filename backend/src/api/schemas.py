"""Pydantic schemas for API requests and responses."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID


# Authentication Schemas
class UserRegister(BaseModel):
    """User registration schema."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserLogin(BaseModel):
    """User login schema."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User response schema."""
    id: UUID
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Transaction Schemas
class TransactionBase(BaseModel):
    """Base transaction schema."""
    date: date
    amount: Decimal
    description: Optional[str] = None
    transaction_type: str
    account_name: Optional[str] = None
    balance: Optional[Decimal] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None


class TransactionCreate(TransactionBase):
    """Transaction creation schema."""
    statement_id: Optional[UUID] = None


class TransactionUpdate(BaseModel):
    """Transaction update schema."""
    category: Optional[str] = None
    subcategory: Optional[str] = None
    account_name: Optional[str] = None
    is_confirmed: Optional[bool] = None


class TransactionResponse(TransactionBase):
    """Transaction response schema."""
    id: UUID
    user_id: UUID
    statement_id: Optional[UUID]
    matched_transaction_id: Optional[UUID]
    match_confidence: Optional[Decimal]
    is_confirmed: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Statement Schemas
class StatementCreate(BaseModel):
    """Statement creation schema."""
    file_name: str
    bank_name: Optional[str] = None
    account_type: Optional[str] = None
    statement_date_start: Optional[date] = None
    statement_date_end: Optional[date] = None


class StatementResponse(BaseModel):
    """Statement response schema."""
    id: UUID
    user_id: UUID
    file_name: str
    bank_name: Optional[str]
    account_type: Optional[str]
    statement_date_start: Optional[date]
    statement_date_end: Optional[date]
    status: str
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


# Category Schemas
class CategoryCreate(BaseModel):
    """Category creation schema."""
    name: str
    parent_category: str  # Asset, Liability, Equity, Income, Expense
    subcategory: Optional[str] = None


class CategoryResponse(BaseModel):
    """Category response schema."""
    id: UUID
    user_id: UUID
    name: str
    parent_category: str
    subcategory: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Filter Schemas
class TransactionFilter(BaseModel):
    """Transaction filter schema."""
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None
    categories: Optional[List[str]] = None
    accounts: Optional[List[str]] = None
    amount_min: Optional[Decimal] = None
    amount_max: Optional[Decimal] = None
    transaction_types: Optional[List[str]] = None
    match_status: Optional[str] = None
    search_text: Optional[str] = None
    vendors: Optional[List[str]] = None


class FilterPresetCreate(BaseModel):
    """Filter preset creation schema."""
    name: str
    filter_config: dict


class FilterPresetResponse(BaseModel):
    """Filter preset response schema."""
    id: UUID
    user_id: UUID
    name: str
    filter_config: dict
    created_at: datetime
    
    class Config:
        from_attributes = True

