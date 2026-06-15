"""
Product Model

Represents inventory items available for purchase.
"""

from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional

from app.config.database import Base


def utc_now():
    """Return current UTC datetime as naive datetime for database"""
    return datetime.utcnow()


class Product(Base):
    """
    Product model for inventory management.
    
    Attributes:
        id: Primary key
        name: Product name
        description: Product description
        price: Current selling price
        stock_quantity: Available inventory count
        category_id: Foreign key to Category
        is_active: Product availability status
        created_at: Creation timestamp
        updated_at: Last update timestamp
        category: Relationship to Category
    """
    
    __tablename__ = "products"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Product information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0, nullable=False)
    
    # Foreign keys
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    
    # Relationships
    category = relationship("Category", back_populates="products", lazy="select")
    
    def __repr__(self) -> str:
        """Simple string representation - avoids database access"""
        return f"<Product(id={self.id})>"
    
    def is_in_stock(self) -> bool:
        """Check if product has stock available"""
        return self.stock_quantity > 0
    
    def is_low_stock(self, threshold: int = 5) -> bool:
        """Check if product stock is below threshold"""
        return self.stock_quantity <= threshold
    
    def can_purchase(self, quantity: int) -> bool:
        """Check if requested quantity can be purchased"""
        return self.is_active and self.stock_quantity >= quantity
    
    def reduce_stock(self, quantity: int) -> bool:
        """
        Reduce stock by given quantity.
        
        Args:
            quantity: Number of units to reduce
            
        Returns:
            bool: True if successful, False if insufficient stock
        """
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            return True
        return False
    
    def increase_stock(self, quantity: int):
        """Increase stock by given quantity"""
        self.stock_quantity += quantity
    
    def to_dict(self) -> dict:
        """Convert product to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "stock_quantity": self.stock_quantity,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "is_active": self.is_active,
            "is_in_stock": self.is_in_stock(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }