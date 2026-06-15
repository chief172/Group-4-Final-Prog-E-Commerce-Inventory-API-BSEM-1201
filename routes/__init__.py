"""
API Routes Module
"""

from .auth_routes import router as auth_router
from .user_routes import router as user_router
from .category_routes import router as category_router
from .product_routes import router as product_router
from .cart_routes import router as cart_router
from .order_routes import router as order_router
from .dashboard_routes import router as dashboard_router
from .admin_routes import router as admin_router

__all__ = [
    "auth_router",
    "user_router",
    "category_router",
    "product_router",
    "cart_router",
    "order_router",
    "dashboard_router",
    "admin_router",
]