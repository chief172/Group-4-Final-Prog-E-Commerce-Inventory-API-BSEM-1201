"""
Cart Item Model

Represents items in a user's shopping cart before checkout.
"""

from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional

from app.config.database import Base


def utc_now():
    """Return current UTC datetime as naive datetime for database"""
    return datetime.utcnow()


class CartItem(Base):
    """
    Shopping cart item model.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User
        product_id: Foreign key to Product
        quantity: Number of units in cart
        created_at: Creation timestamp
        updated_at: Last update timestamp
        user: Relationship to User
        product: Relationship to Product
    """
    
    __tablename__ = "cart_items"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Quantity
    quantity = Column(Integer, default=1, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    
    # Relationships
    user = relationship("User", lazy="select")
    product = relationship("Product", lazy="select")
    
    def __repr__(self) -> str:
        """Simple string representation - avoids database access"""
        return f"<CartItem(id={self.id}, user_id={self.user_id})>"
    
    def subtotal(self) -> float:
        """Calculate subtotal for this cart item"""
        if self.product:
            return self.product.price * self.quantity
        return 0.0
    
    def increase_quantity(self, amount: int = 1):
        """Increase quantity by specified amount"""
        if amount > 0:
            self.quantity += amount
    
    def decrease_quantity(self, amount: int = 1):
        """Decrease quantity by specified amount"""
        if amount > 0 and self.quantity >= amount:
            self.quantity -= amount
    
    def to_dict(self) -> dict:
        """Convert cart item to dictionary with product details"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "subtotal": self.subtotal(),
            "product_name": self.product.name if self.product else None,
            "product_price": self.product.price if self.product else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }