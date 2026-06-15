"""
E-Commerce Inventory API

A professional-grade REST API for inventory management supporting SDG 8:
Decent Work and Economic Growth in Sierra Leone.
"""

__version__ = "2.0.0"
__author__ = "BSEM 1201 Group 4"
__license__ = "MIT"

# Import only what's needed for the package
from .config.database import get_db, init_db, close_db
from .auth import JWTBearer, create_access_token, verify_token

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    
    # Database
    "get_db",
    "init_db",
    "close_db",
    
    # Auth
    "JWTBearer",
    "create_access_token",
    "verify_token",
]