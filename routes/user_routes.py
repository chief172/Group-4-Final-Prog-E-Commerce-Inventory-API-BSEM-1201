"""
User Management Routes

Handles admin operations for user accounts.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List

from app.config.database import get_db
from app.models.user_model import User
from app.schemas.user_schema import UserResponse
from app.auth.role import admin_required

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """
    Get all users (Admin only).
    
    Returns list of all registered users.
    """
    
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """
    Get user by ID (Admin only).
    
    - **user_id**: ID of the user to retrieve
    """
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return user


@router.put("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """
    Deactivate a user account (Admin only).
    
    Deactivated users cannot log in.
    """
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    user.is_active = False
    await db.commit()
    await db.refresh(user)
    
    return user


@router.put("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """
    Activate a user account (Admin only).
    
    Reactivates a previously deactivated user.
    """
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    user.is_active = True
    await db.commit()
    await db.refresh(user)
    
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """
    Delete a user account (Admin only).
    
    This permanently removes the user from the database.
    """
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    await db.delete(user)
    await db.commit()