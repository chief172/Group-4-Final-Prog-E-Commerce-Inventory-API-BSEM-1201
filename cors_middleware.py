"""
CORS Middleware Configuration

This module provides enhanced CORS configuration for the API.
"""

from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import CORS_ALLOWED_ORIGINS


def configure_cors(app):
    """
    Configure CORS middleware for the application.
    
    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Request-ID",
            "X-API-Key",
            "Accept",
            "Origin",
            "User-Agent"
        ],
        expose_headers=[
            "X-Request-ID",
            "X-Response-Time-MS",
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset"
        ],
        max_age=3600,  # Cache preflight requests for 1 hour
    )
    
    return app