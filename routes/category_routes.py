"""
Category Management Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.config.database import get_db
from app.models.category_model import Category
from app.schemas.category_schema import CategoryCreate, CategoryUpdate, CategoryResponse

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get all categories"""
    result = await db.execute(
        select(Category).offset(skip).limit(limit).order_by(Category.name)
    )
    categories = result.scalars().all()
    return categories


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get category by ID"""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    
    return category


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new category"""
    
    result = await db.execute(select(Category).where(Category.name == category.name))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category '{category.name}' already exists"
        )
    
    new_category = Category(
        name=category.name,
        description=category.description
    )
    
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    
    return new_category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a category"""
    
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    
    if category_data.name:
        result = await db.execute(
            select(Category).where(Category.name == category_data.name)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category '{category_data.name}' already exists"
            )
        category.name = category_data.name
    
    if category_data.description:
        category.description = category_data.description
    
    await db.commit()
    await db.refresh(category)
    
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a category"""
    
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    
    await db.delete(category)
    await db.commit()