"""
Cart Schemas

Pydantic models for shopping cart request/response validation.
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List


class CartCreate(BaseModel):
    """
    Schema for adding item to cart.
    
    Attributes:
        user_id: User ID
        product_id: Product ID
        quantity: Quantity (1-100)
    """
    
    user_id: int = Field(
        ...,
        gt=0,
        description="User ID",
        example=1
    )
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
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "product_id": 1,
                "quantity": 2
            }
        }


class CartUpdate(BaseModel):
    """
    Schema for updating cart item quantity.
    
    Attributes:
        quantity: New quantity (1-100)
    """
    
    quantity: int = Field(
        ...,
        ge=1,
        le=100,
        description="New quantity (1-100)",
        example=3
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
    
    class Config:
        json_schema_extra = {
            "example": {
                "quantity": 3
            }
        }


class CartResponse(BaseModel):
    """
    Schema for cart item response.
    
    Attributes:
        id: Cart item ID
        user_id: User ID
        product_id: Product ID
        quantity: Quantity
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    id: int = Field(..., description="Cart item ID", example=1)
    user_id: int = Field(..., description="User ID", example=1)
    product_id: int = Field(..., description="Product ID", example=1)
    quantity: int = Field(..., description="Quantity", example=2)
    created_at: datetime = Field(..., description="Creation date")
    updated_at: Optional[datetime] = Field(None, description="Last update date")
    
    class Config:
        from_attributes = True


class CartItemResponse(BaseModel):
    """
    Schema for detailed cart item response with product info.
    
    Attributes:
        id: Cart item ID
        product_id: Product ID
        product_name: Product name
        product_price: Product price
        quantity: Quantity
        subtotal: Item subtotal
        in_stock: Whether product is in stock
    """
    
    id: int = Field(..., description="Cart item ID")
    product_id: int = Field(..., description="Product ID")
    product_name: str = Field(..., description="Product name")
    product_price: float = Field(..., description="Product price")
    quantity: int = Field(..., description="Quantity")
    subtotal: float = Field(..., description="Item subtotal")
    in_stock: bool = Field(..., description="Product in stock")
    
    class Config:
        from_attributes = True


class CartDetailResponse(BaseModel):
    """
    Schema for complete cart response.
    
    Attributes:
        user_id: User ID
        items: List of cart items with details
        total_items: Total number of items
        total_amount: Total cart value
    """
    
    user_id: int = Field(..., description="User ID")
    items: List[CartItemResponse] = Field(default_factory=list, description="Cart items")
    total_items: int = Field(0, description="Total number of items")
    total_amount: float = Field(0.0, description="Total cart value")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "items": [
                    {
                        "id": 1,
                        "product_id": 1,
                        "product_name": "Smartphone X",
                        "product_price": 599.99,
                        "quantity": 2,
                        "subtotal": 1199.98,
                        "in_stock": True
                    }
                ],
                "total_items": 2,
                "total_amount": 1199.98
            }
        }