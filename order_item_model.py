"""
Order Item Model

Represents individual items within an order.
"""

from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional

from app.config.database import Base


def utc_now():
    """Return current UTC datetime as naive datetime for database"""
    return datetime.utcnow()


class OrderItem(Base):
    """
    Order item model - snapshot of product at purchase time.
    
    Attributes:
        id: Primary key
        order_id: Foreign key to Order
        product_id: Foreign key to Product
        quantity: Number of units purchased
        price: Price at time of purchase (snapshot)
        created_at: Creation timestamp
        order: Relationship to Order
        product: Relationship to Product
    """
    
    __tablename__ = "order_items"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign keys
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Item details (snapshot at purchase time)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    
    # Timestamp
    created_at = Column(DateTime, default=utc_now, nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="items", lazy="select")
    product = relationship("Product", lazy="select")
    
    def __repr__(self) -> str:
        """Simple string representation - avoids database access"""
        return f"<OrderItem(id={self.id}, order_id={self.order_id})>"
    
    def subtotal(self) -> float:
        """Calculate subtotal for this order item"""
        return self.price * self.quantity
    
    def product_name(self) -> Optional[str]:
        """Get product name"""
        return self.product.name if self.product else None
    
    def to_dict(self) -> dict:
        """Convert order item to dictionary with product details"""
        return {
            "id": self.id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "price": self.price,
            "subtotal": self.subtotal(),
            "product_name": self.product_name(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }