"""
User Schemas

Pydantic models for user-related request/response validation.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional, List


class UserCreate(BaseModel):
    """
    Schema for user registration request.
    
    Attributes:
        username: Display name (3-50 characters, alphanumeric + underscore)
        email: Valid email address
        password: Password (min 6 characters)
        role: User role - can be 'admin' or 'customer' (default: 'customer')
    """
    
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r'^[a-zA-Z0-9_]+$',
        description="Username (alphanumeric and underscore only)",
        example="john_doe"
    )
    email: EmailStr = Field(
        ...,
        description="Valid email address",
        example="john@example.com"
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="Password (minimum 6 characters)",
        example="secure_password123",
        write_only=True
    )
    role: Optional[str] = Field(
        default="customer",
        pattern="^(admin|customer)$",
        description="User role (admin or customer)",
        example="customer"
    )
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format"""
        if not v.replace("_", "").isalnum():
            raise ValueError("Username must contain only letters, numbers, and underscores")
        return v.lower()
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "secure_password123",
                "role": "customer"
            }
        }


class UserLogin(BaseModel):
    """
    Schema for user login request.
    
    Attributes:
        email: User's email address
        password: User's password
    """
    
    email: EmailStr = Field(
        ...,
        description="Registered email address",
        example="john@example.com"
    )
    password: str = Field(
        ...,
        description="Account password",
        example="secure_password123",
        write_only=True
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "password": "secure_password123"
            }
        }


class UserUpdate(BaseModel):
    """
    Schema for user update request.
    
    Attributes:
        username: Updated username (optional)
        email: Updated email (optional)
        is_active: Account status (admin only)
        role: User role (admin only)
    """
    
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        pattern=r'^[a-zA-Z0-9_]+$',
        description="New username"
    )
    email: Optional[EmailStr] = Field(
        None,
        description="New email address"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Account active status"
    )
    role: Optional[str] = Field(
        None,
        pattern="^(admin|customer)$",
        description="User role (admin or customer)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_updated",
                "email": "john_new@example.com"
            }
        }


class UserResponse(BaseModel):
    """
    Schema for user response.
    
    Attributes:
        id: User ID
        username: Display name
        email: Email address
        role: User role (admin/customer)
        is_active: Account status
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    
    id: int = Field(..., description="Unique user ID", example=1)
    username: str = Field(..., description="Username", example="john_doe")
    email: EmailStr = Field(..., description="Email address", example="john@example.com")
    role: str = Field(..., description="User role", example="customer")
    is_active: bool = Field(..., description="Account active status", example=True)
    created_at: datetime = Field(..., description="Account creation date")
    updated_at: Optional[datetime] = Field(None, description="Last update date")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "role": "customer",
                "is_active": True,
                "created_at": "2026-01-15T10:30:00Z",
                "updated_at": "2026-01-15T10:30:00Z"
            }
        }


class TokenResponse(BaseModel):
    """
    Schema for JWT token response.
    
    Attributes:
        access_token: JWT token string
        token_type: Token type (bearer)
        expires_in: Token expiration in seconds
        user: User information
    """
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds", example=1800)
    user: UserResponse = Field(..., description="Authenticated user info")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIs...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "id": 1,
                    "username": "john_doe",
                    "email": "john@example.com",
                    "role": "customer"
                }
            }
        }