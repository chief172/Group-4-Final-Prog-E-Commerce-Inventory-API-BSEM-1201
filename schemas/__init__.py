"""
Pydantic Schemas Module for E-Commerce Inventory API

This module contains all request/response validation schemas:
- User schemas (registration, login, response)
- Category schemas (create, update, response)
- Product schemas (create, update, response)
- Cart schemas (create, update, response)
- Order schemas (create, response)

All schemas use Pydantic for automatic validation, serialization,
and OpenAPI documentation generation.
"""

from .user_schema import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate
)
from .category_schema import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse
)
from .product_schema import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductLowStockResponse
)
from .cart_schema import (
    CartCreate,
    CartUpdate,
    CartResponse,
    CartItemResponse
)
from .order_schema import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderItemCreate,
    OrderItemResponse
)

__all__ = [
    # User
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "UserUpdate",
    # Category
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    # Product
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "ProductLowStockResponse",
    # Cart
    "CartCreate",
    "CartUpdate",
    "CartResponse",
    "CartItemResponse",
    # Order
    "OrderCreate",
    "OrderUpdate",
    "OrderResponse",
    "OrderItemCreate",
    "OrderItemResponse",
]