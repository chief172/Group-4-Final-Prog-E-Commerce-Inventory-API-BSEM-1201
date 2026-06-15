"""
Services Module for E-Commerce Inventory API

This module contains business logic services:
- Authentication Service: User registration, login, token management
- Inventory Service: Stock management, product availability
- Order Service: Order processing, validation, status updates
- Analytics Service: Sales reports, dashboard statistics
"""

from .auth_service import AuthService
from .inventory_service import InventoryService
from .order_service import OrderService
from .analytics_service import AnalyticsService

__all__ = [
    "AuthService",
    "InventoryService", 
    "OrderService",
    "AnalyticsService",
]