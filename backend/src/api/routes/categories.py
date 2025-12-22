"""Category routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from src.database.connection import get_db
from src.database.models import User, Category
from src.auth.middleware import get_current_active_user
from src.api.schemas import CategoryCreate, CategoryResponse
from src.categorization.category_manager import CategoryManager

router = APIRouter(prefix="/api/categories", tags=["categories"])
category_manager = CategoryManager()


@router.get("", response_model=List[CategoryResponse])
async def get_categories(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all categories for the current user."""
    categories = db.query(Category).filter(
        Category.user_id == current_user.id
    ).all()
    return categories


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new category."""
    # Validate parent category
    if category_data.parent_category not in category_manager.FINANCIAL_COMPONENTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Parent category must be one of: {', '.join(category_manager.FINANCIAL_COMPONENTS)}"
        )
    
    category = Category(
        user_id=current_user.id,
        name=category_data.name,
        parent_category=category_data.parent_category,
        subcategory=category_data.subcategory
    )
    
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return category


@router.post("/bulk-assign")
async def bulk_assign_category(
    vendor_pattern: str,
    category: str,
    subcategory: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Bulk assign category to transactions matching vendor pattern."""
    count = category_manager.bulk_assign_by_vendor(
        db=db,
        vendor_pattern=vendor_pattern,
        category=category,
        subcategory=subcategory,
        user_id=str(current_user.id)
    )
    
    return {
        "message": f"Assigned category to {count} transactions",
        "count": count
    }

