"""Category management and assignment."""
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from src.database.models import Category, LearningPattern, Transaction
from src.models.transaction import Transaction as TransactionModel


class CategoryManager:
    """Manages transaction categorization."""
    
    FINANCIAL_COMPONENTS = ["Asset", "Liability", "Equity", "Income", "Expense"]
    
    def assign_category(
        self,
        db: Session,
        transaction_id: str,
        category: str,
        subcategory: Optional[str] = None,
        user_id: str = None
    ) -> bool:
        """Assign category to a transaction."""
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not transaction:
            return False
        
        transaction.category = category
        transaction.subcategory = subcategory
        
        # Learn from this assignment
        if user_id:
            self._learn_from_assignment(db, transaction, category, user_id)
        
        db.commit()
        return True
    
    def bulk_assign_by_vendor(
        self,
        db: Session,
        vendor_pattern: str,
        category: str,
        subcategory: Optional[str] = None,
        user_id: str = None
    ) -> int:
        """Bulk assign category to all transactions matching vendor pattern."""
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.description.ilike(f"%{vendor_pattern}%")
        ).all()
        
        count = 0
        for transaction in transactions:
            transaction.category = category
            transaction.subcategory = subcategory
            count += 1
            
            # Learn from assignment
            if user_id:
                self._learn_from_assignment(db, transaction, category, user_id)
        
        db.commit()
        return count
    
    def suggest_category(
        self,
        db: Session,
        transaction: TransactionModel,
        user_id: str
    ) -> Tuple[Optional[str], float]:
        """Suggest category for a transaction based on learning patterns."""
        best_category = None
        best_confidence = 0.0
        
        if not transaction.description:
            return None, 0.0
        
        description_upper = transaction.description.upper()
        
        # Check vendor patterns
        vendor_patterns = db.query(LearningPattern).filter(
            LearningPattern.user_id == user_id,
            LearningPattern.pattern_type == "vendor"
        ).all()
        
        for pattern in vendor_patterns:
            if pattern.pattern_value.upper() in description_upper:
                category = db.query(Category).filter(Category.id == pattern.category_id).first()
                if category:
                    confidence = float(pattern.confidence) * (pattern.usage_count / 100.0)
                    if confidence > best_confidence:
                        best_category = category.parent_category
                        best_confidence = min(confidence, 1.0)
        
        # Check keyword patterns
        keyword_patterns = db.query(LearningPattern).filter(
            LearningPattern.user_id == user_id,
            LearningPattern.pattern_type == "keyword"
        ).all()
        
        for pattern in keyword_patterns:
            if pattern.pattern_value.upper() in description_upper:
                category = db.query(Category).filter(Category.id == pattern.category_id).first()
                if category:
                    confidence = float(pattern.confidence) * 0.7  # Keywords are less reliable
                    if confidence > best_confidence:
                        best_category = category.parent_category
                        best_confidence = min(confidence, 1.0)
        
        return best_category, best_confidence
    
    def _learn_from_assignment(
        self,
        db: Session,
        transaction: Transaction,
        category: str,
        user_id: str
    ):
        """Learn from user's category assignment."""
        if not transaction.description:
            return
        
        description_upper = transaction.description.upper()
        
        # Extract vendor name (simplified - first few words)
        words = transaction.description.split()[:3]
        vendor = " ".join(words).upper()
        
        # Find or create learning pattern
        pattern = db.query(LearningPattern).filter(
            LearningPattern.user_id == user_id,
            LearningPattern.pattern_type == "vendor",
            LearningPattern.pattern_value == vendor
        ).first()
        
        category_obj = db.query(Category).filter(
            Category.user_id == user_id,
            Category.parent_category == category
        ).first()
        
        if pattern:
            # Update existing pattern
            pattern.usage_count += 1
            pattern.confidence = min(float(pattern.confidence) + 0.1, 1.0)
            pattern.last_used = transaction.date
        else:
            # Create new pattern
            pattern = LearningPattern(
                user_id=user_id,
                pattern_type="vendor",
                pattern_value=vendor,
                category_id=category_obj.id if category_obj else None,
                confidence=0.7,
                usage_count=1
            )
            db.add(pattern)
        
        db.commit()

