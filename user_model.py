"""
User Model

Represents application users with authentication and role-based access control.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import List, Optional

from app.config.database import Base


def utc_now():
    """Return current UTC datetime as naive datetime for database"""
    return datetime.utcnow()


class User(Base):
    """
    User model for authentication and authorization.
    
    Attributes:
        id: Primary key
        username: Display name (unique)
        email: Email address for login (unique)
        password: Hashed password (never store plain text)
        role: User role - 'admin' or 'customer'
        is_active: Account status
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        orders: Relationship to user's orders
    """
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # User information
    username = Column(String(100), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)  # Hashed with bcrypt
    
    # Role and status
    role = Column(String(20), default="customer", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    
    # Relationships
    orders = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        """Simple string representation - avoids database access"""
        return f"<User(id={self.id}, email={self.email})>"
    
    def is_admin(self) -> bool:
        """Check if user has admin role"""
        return self.role == "admin"
    
    def is_customer(self) -> bool:
        """Check if user has customer role"""
        return self.role == "customer"
    
    def to_dict(self) -> dict:
        """Convert user to dictionary (excludes sensitive data)"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }