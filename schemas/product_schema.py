"""
Product Schemas

Pydantic models for product-related request/response validation.
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List


class ProductCreate(BaseModel):
    """
    Schema for product creation request.
    
    Attributes:
        name: Product name (2-255 characters)
        description: Product description
        price: Selling price (> 0)
        stock_quantity: Initial inventory (>= 0)
        category_id: Category ID
    """
    
    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Product name",
        example="Smartphone X"
    )
    description: str = Field(
        ...,
        max_length=2000,
        description="Product description",
        example="Latest smartphone with advanced features"
    )
    price: float = Field(
        ...,
        gt=0,
        le=100000,
        description="Product price (> 0)",
        example=599.99
    )
    stock_quantity: int = Field(
        ...,
        ge=0,
        le=999999,
        description="Available stock quantity",
        example=100
    )
    category_id: int = Field(
        ...,
        gt=0,
        description="Category ID",
        example=1
    )
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate product name"""
        v = v.strip()
        if not v:
            raise ValueError("Product name cannot be empty")
        return v
    
    @field_validator("price")
    @classmethod
    def validate_price(cls, v: float) -> float:
        """Validate price"""
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return round(v, 2)
    
    @field_validator("stock_quantity")
    @classmethod
    def validate_stock(cls, v: int) -> int:
        """Validate stock quantity"""
        if v < 0:
            raise ValueError("Stock quantity cannot be negative")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Smartphone X",
                "description": "Latest smartphone with 128GB storage and 5G",
                "price": 599.99,
                "stock_quantity": 100,
                "category_id": 1
            }
        }


class ProductUpdate(BaseModel):
    """
    Schema for product update request.
    
    Attributes:
        name: Updated product name
        description: Updated description
        price: Updated price
        stock_quantity: Updated stock
        category_id: Updated category
        is_active: Product status
    """
    
    name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=255,
        description="Updated product name"
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Updated description"
    )
    price: Optional[float] = Field(
        None,
        gt=0,
        le=100000,
        description="Updated price"
    )
    stock_quantity: Optional[int] = Field(
        None,
        ge=0,
        le=999999,
        description="Updated stock quantity"
    )
    category_id: Optional[int] = Field(
        None,
        gt=0,
        description="Updated category ID"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Product active status"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Smartphone X Pro",
                "price": 699.99,
                "stock_quantity": 50
            }
        }


class ProductResponse(BaseModel):
    """
    Schema for product response.
    
    Attributes:
        id: Product ID
        name: Product name
        description: Product description
        price: Current price
        stock_quantity: Available stock
        category_id: Category ID
        category_name: Category name (from relationship)
        is_active: Product status
        is_in_stock: Whether product has stock
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    id: int = Field(..., description="Unique product ID", example=1)
    name: str = Field(..., description="Product name", example="Smartphone X")
    description: str = Field(..., description="Product description")
    price: float = Field(..., description="Current price", example=599.99)
    stock_quantity: int = Field(..., description="Available stock", example=100)
    category_id: int = Field(..., description="Category ID", example=1)
    category_name: Optional[str] = Field(None, description="Category name")
    is_active: bool = Field(..., description="Product active status", example=True)
    is_in_stock: bool = Field(..., description="Product in stock", example=True)
    created_at: datetime = Field(..., description="Creation date")
    updated_at: Optional[datetime] = Field(None, description="Last update date")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Smartphone X",
                "description": "Latest smartphone with advanced features",
                "price": 599.99,
                "stock_quantity": 100,
                "category_id": 1,
                "category_name": "Electronics",
                "is_active": True,
                "is_in_stock": True,
                "created_at": "2026-01-15T10:30:00Z",
                "updated_at": "2026-01-15T10:30:00Z"
            }
        }


class ProductLowStockResponse(BaseModel):
    """
    Schema for low stock product alert response.
    
    Attributes:
        id: Product ID
        name: Product name
        stock_quantity: Current stock
        price: Product price
        category_name: Category name
    """
    
    id: int = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    stock_quantity: int = Field(..., description="Current stock quantity")
    price: float = Field(..., description="Product price")
    category_name: Optional[str] = Field(None, description="Category name")
    
    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """
    Schema for paginated product list response.
    
    Attributes:
        total: Total number of products
        skip: Number of skipped records
        limit: Records per page
        filters: Applied filters
        items: List of products
    """
    
    total: int = Field(..., description="Total products count")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Records per page")
    filters: dict = Field(default_factory=dict, description="Applied filters")
    items: List[ProductResponse] = Field(..., description="List of products")