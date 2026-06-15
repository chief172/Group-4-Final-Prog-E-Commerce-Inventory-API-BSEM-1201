"""
Category Model

Represents product categories for organizing inventory.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import List, Optional

from app.config.database import Base


def utc_now():
    """Return current UTC datetime as naive datetime for database"""
    return datetime.utcnow()


class Category(Base):
    """
    Category model for product organization.
    
    Attributes:
        id: Primary key
        name: Category name (unique)
        description: Detailed category description
        created_at: Creation timestamp
        products: Relationship to products in this category
    """
    
    __tablename__ = "categories"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Category information
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=utc_now, nullable=False)
    
    # Relationships
    products = relationship(
        "Product",
        back_populates="category",
        cascade="all, delete-orphan",
        lazy="select",
        order_by="Product.name"
    )
    
    def __repr__(self) -> str:
        """Simple string representation - avoids database access"""
        return f"<Category(id={self.id})>"
    
    def product_count(self) -> int:
        """Get number of products in this category"""
        return len(self.products) if self.products else 0
    
    def to_dict(self) -> dict:
        """Convert category to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "product_count": self.product_count(),
        }