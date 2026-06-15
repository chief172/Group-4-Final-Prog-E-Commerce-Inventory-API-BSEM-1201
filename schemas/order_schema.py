"""
Order Schemas

Pydantic models for order-related request/response validation.
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List


class OrderItemCreate(BaseModel):
    """
    Schema for creating an order item.
    
    Attributes:
        product_id: Product ID
        quantity: Quantity (1-100)
    """
    
    product_id: int = Field(
        ...,
        gt=0,
        description="Product ID",
        example=1
    )
    quantity: int = Field(
        ...,
        ge=1,
        le=100,
        description="Quantity (1-100)",
        example=2
    )
    
    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        """Validate quantity"""
        if v < 1:
            raise ValueError("Quantity must be at least 1")
        if v > 100:
            raise ValueError("Quantity cannot exceed 100")
        return v


class OrderCreate(BaseModel):
    """
    Schema for creating an order.
    
    Attributes:
        user_id: User ID
        items: List of order items
    """
    
    user_id: int = Field(
        ...,
        gt=0,
        description="User ID",
        example=1
    )
    items: List[OrderItemCreate] = Field(
        ...,
        min_length=1,
        description="List of order items"
    )
    
    @field_validator("items")
    @classmethod
    def validate_items(cls, v: List[OrderItemCreate]) -> List[OrderItemCreate]:
        """Validate order items"""
        if not v:
            raise ValueError("Order must contain at least one item")
        
        # Check for duplicate products
        product_ids = [item.product_id for item in v]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError("Duplicate products in order")
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "items": [
                    {"product_id": 1, "quantity": 2},
                    {"product_id": 2, "quantity": 1}
                ]
            }
        }


class OrderUpdate(BaseModel):
    """
    Schema for updating an order.
    
    Attributes:
        status: Order status
    """
    
    status: str = Field(
        ...,
        pattern="^(Pending|Processing|Shipped|Delivered|Cancelled)$",
        description="Order status",
        example="Processing"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "Processing"
            }
        }


class OrderItemResponse(BaseModel):
    """
    Schema for order item response.
    
    Attributes:
        id: Order item ID
        product_id: Product ID
        product_name: Product name
        quantity: Quantity
        price: Price at purchase
        subtotal: Item subtotal
    """
    
    id: int = Field(..., description="Order item ID")
    product_id: int = Field(..., description="Product ID")
    product_name: Optional[str] = Field(None, description="Product name")
    quantity: int = Field(..., description="Quantity")
    price: float = Field(..., description="Price at purchase")
    subtotal: float = Field(..., description="Item subtotal")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "product_id": 1,
                "product_name": "Smartphone X",
                "quantity": 2,
                "price": 599.99,
                "subtotal": 1199.98
            }
        }


class OrderResponse(BaseModel):
    """
    Schema for order response.
    
    Attributes:
        id: Order ID
        user_id: User ID
        user_name: Username
        total_amount: Total order amount
        status: Order status
        item_count: Number of items in order
        created_at: Creation timestamp
        updated_at: Last update timestamp
        items: List of order items
    """
    
    id: int = Field(..., description="Order ID", example=1)
    user_id: int = Field(..., description="User ID", example=1)
    user_name: Optional[str] = Field(None, description="Username")
    total_amount: float = Field(..., description="Total order amount", example=1199.98)
    status: str = Field(..., description="Order status", example="Pending")
    item_count: int = Field(0, description="Number of items in order")
    created_at: datetime = Field(..., description="Creation date")
    updated_at: Optional[datetime] = Field(None, description="Last update date")
    items: List[OrderItemResponse] = Field(default_factory=list, description="Order items")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "user_name": "john_doe",
                "total_amount": 1199.98,
                "status": "Delivered",
                "item_count": 2,
                "created_at": "2026-01-15T10:30:00Z",
                "updated_at": "2026-01-16T14:20:00Z",
                "items": [
                    {
                        "id": 1,
                        "product_id": 1,
                        "product_name": "Smartphone X",
                        "quantity": 2,
                        "price": 599.99,
                        "subtotal": 1199.98
                    }
                ]
            }
        }


class OrderListResponse(BaseModel):
    """
    Schema for paginated order list response.
    
    Attributes:
        total: Total number of orders
        skip: Number of skipped records
        limit: Records per page
        items: List of orders
    """
    
    total: int = Field(..., description="Total orders count")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Records per page")
    items: List[OrderResponse] = Field(..., description="List of orders")