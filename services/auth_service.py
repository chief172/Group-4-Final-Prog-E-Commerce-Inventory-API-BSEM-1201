"""
Authentication Service

Handles business logic for user authentication:
- User registration with validation
- Login with password verification
- JWT token generation and validation
- User account management
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from typing import Optional, Dict, Any

from app.models.user_model import User
from app.auth.password_handler import hash_password, verify_password
from app.auth.jwt_handler import create_access_token, verify_token


class AuthService:
    """
    Service class for authentication operations.
    """
    
    @staticmethod
    async def register_user(
        db: AsyncSession,
        username: str,
        email: str,
        password: str
    ) -> User:
        """
        Register a new user.
        
        Args:
            db: Database session
            username: User's chosen username
            email: User's email address
            password: Plain text password
            
        Returns:
            User: Created user object
            
        Raises:
            HTTPException: If email or username already exists
        """
        
        # Check if email exists
        result = await db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username exists
        result = await db.execute(select(User).where(User.username == username))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password=hash_password(password),
            role="customer",
            is_active=True
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        return new_user
    
    @staticmethod
    async def login_user(
        db: AsyncSession,
        email: str,
        password: str
    ) -> Dict[str, Any]:
        """
        Authenticate user and generate access token.
        
        Args:
            db: Database session
            email: User's email
            password: User's password
            
        Returns:
            Dict: Access token and user info
            
        Raises:
            HTTPException: If credentials are invalid
        """
        
        # Find user by email
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated. Please contact support."
            )
        
        # Generate access token
        access_token = create_access_token({
            "sub": user.email,
            "role": user.role,
            "user_id": user.id,
            "username": user.username
        })
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 1800,  # 30 minutes
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }
    
    @staticmethod
    async def get_current_user(
        db: AsyncSession,
        token: str
    ) -> Optional[User]:
        """
        Get current user from JWT token.
        
        Args:
            db: Database session
            token: JWT token string
            
        Returns:
            User: Authenticated user or None
        """
        
        payload = verify_token(token)
        
        if not payload:
            return None
        
        email = payload.get("sub")
        
        if not email:
            return None
        
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        return user
    
    @staticmethod
    async def change_password(
        db: AsyncSession,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        Change user's password.
        
        Args:
            db: Database session
            user_id: User ID
            old_password: Current password
            new_password: New password
            
        Returns:
            bool: True if password changed successfully
            
        Raises:
            HTTPException: If old password is incorrect
        """
        
        # Get user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify old password
        if not verify_password(old_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password"
            )
        
        # Update password
        user.password = hash_password(new_password)
        await db.commit()
        
        return True
    
    @staticmethod
    async def deactivate_user(
        db: AsyncSession,
        user_id: int,
        admin_id: int
    ) -> bool:
        """
        Deactivate a user account (admin only).
        
        Args:
            db: Database session
            user_id: User to deactivate
            admin_id: Admin performing action
            
        Returns:
            bool: True if deactivated successfully
        """
        
        # Verify admin exists
        result = await db.execute(select(User).where(User.id == admin_id))
        admin = result.scalar_one_or_none()
        
        if not admin or admin.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        # Get user to deactivate
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Cannot deactivate admin
        if user.role == "admin":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate admin account"
            )
        
        user.is_active = False
        await db.commit()
        
        return True
    
    @staticmethod
    async def activate_user(
        db: AsyncSession,
        user_id: int,
        admin_id: int
    ) -> bool:
        """
        Activate a user account (admin only).
        
        Args:
            db: Database session
            user_id: User to activate
            admin_id: Admin performing action
            
        Returns:
            bool: True if activated successfully
        """
        
        # Verify admin exists
        result = await db.execute(select(User).where(User.id == admin_id))
        admin = result.scalar_one_or_none()
        
        if not admin or admin.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        # Get user to activate
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = True
        await db.commit()
        
        return True