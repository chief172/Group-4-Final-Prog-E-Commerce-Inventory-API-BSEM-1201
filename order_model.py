"""
Order Model

Represents customer orders after checkout.
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import List, Optional

from app.config.database import Base


def utc_now():
    """Return current UTC datetime as naive datetime for database"""
    return datetime.utcnow()


class Order(Base):
    """
    Order model for customer purchases.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User
        total_amount: Total order value
        status: Order status (Pending, Processing, Shipped, Delivered, Cancelled)
        created_at: Order creation timestamp
        updated_at: Last update timestamp
        user: Relationship to User
        items: Relationship to OrderItems
    """
    
    __tablename__ = "orders"
    
    # Order status constants
    STATUS_PENDING = "Pending"
    STATUS_PROCESSING = "Processing"
    STATUS_SHIPPED = "Shipped"
    STATUS_DELIVERED = "Delivered"
    STATUS_CANCELLED = "Cancelled"
    
    VALID_STATUSES = [
        STATUS_PENDING,
        STATUS_PROCESSING,
        STATUS_SHIPPED,
        STATUS_DELIVERED,
        STATUS_CANCELLED,
    ]
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Order information
    total_amount = Column(Float, default=0.0, nullable=False)
    status = Column(String(50), default=STATUS_PENDING, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="orders", lazy="select")
    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="select",
        order_by="OrderItem.id"
    )
    
    def __repr__(self) -> str:
        """Simple string representation - avoids database access"""
        return f"<Order(id={self.id}, status={self.status})>"
    
    def can_cancel(self) -> bool:
        """Check if order can be cancelled"""
        return self.status in [self.STATUS_PENDING, self.STATUS_PROCESSING]
    
    def can_update_status(self, new_status: str) -> bool:
        """Check if status update is valid"""
        return new_status in self.VALID_STATUSES
    
    def cancel(self) -> bool:
        """Cancel the order if possible"""
        if self.can_cancel():
            self.status = self.STATUS_CANCELLED
            return True
        return False
    
    def update_status(self, new_status: str) -> bool:
        """Update order status if valid"""
        if self.can_update_status(new_status):
            self.status = new_status
            return True
        return False
    
    def item_count(self) -> int:
        """Get total number of items in order"""
        return sum(item.quantity for item in self.items) if self.items else 0
    
    def to_dict(self) -> dict:
        """Convert order to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.username if self.user else None,
            "total_amount": self.total_amount,
            "status": self.status,
            "item_count": self.item_count(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }