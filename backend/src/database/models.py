"""Database models for the application."""
from sqlalchemy import Column, String, Integer, Float, Date, DateTime, Boolean, Text, ForeignKey, JSON, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from src.database.connection import Base


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    statements = relationship("Statement", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    learning_patterns = relationship("LearningPattern", back_populates="user", cascade="all, delete-orphan")
    filter_presets = relationship("FilterPreset", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")


class Statement(Base):
    """Bank statement model."""
    __tablename__ = "statements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500))
    bank_name = Column(String(100))
    account_type = Column(String(50))
    statement_date_start = Column(Date)
    statement_date_end = Column(Date)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    parsed_at = Column(DateTime)
    status = Column(String(50), default="uploaded")
    
    # Relationships
    user = relationship("User", back_populates="statements")
    transactions = relationship("Transaction", back_populates="statement", cascade="all, delete-orphan")


class Transaction(Base):
    """Transaction model."""
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    statement_id = Column(UUID(as_uuid=True), ForeignKey("statements.id", ondelete="CASCADE"), nullable=True)
    date = Column(Date, nullable=False, index=True)
    amount = Column(DECIMAL(15, 2), nullable=False)
    description = Column(Text)
    transaction_type = Column(String(20), nullable=False)  # 'Paid In' or 'Paid Out'
    account_name = Column(String(255), index=True)
    balance = Column(DECIMAL(15, 2))
    category = Column(String(50), index=True)
    subcategory = Column(String(100))
    matched_transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=True)
    match_confidence = Column(DECIMAL(5, 2))
    is_confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    statement = relationship("Statement", back_populates="transactions")
    matched_transaction = relationship("Transaction", remote_side=[id])


class Account(Base):
    """Account model."""
    __tablename__ = "accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    account_type = Column(String(50))
    parent_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="accounts")
    parent_account = relationship("Account", remote_side=[id])


class Category(Base):
    """Category model."""
    __tablename__ = "categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    parent_category = Column(String(50))  # Asset, Liability, Equity, Income, Expense
    subcategory = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="categories")


class LearningPattern(Base):
    """Learning pattern for categorization."""
    __tablename__ = "learning_patterns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    pattern_type = Column(String(50))  # 'vendor', 'keyword', 'amount_range'
    pattern_value = Column(String(255))
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    confidence = Column(DECIMAL(5, 2))
    usage_count = Column(Integer, default=1)
    last_used = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="learning_patterns")
    category = relationship("Category")


class FilterPreset(Base):
    """Saved filter preset."""
    __tablename__ = "filter_presets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    filter_config = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="filter_presets")


class Session(Base):
    """User session model."""
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sessions")

