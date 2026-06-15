"""
Authentication Middleware - Validates JWT tokens
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware that validates JWT tokens"""
    
    PUBLIC_PATHS = [
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/auth/register",
        "/auth/login",
    ]
    
    async def dispatch(self, request: Request, call_next):
        # Check if path is public
        is_public = any(request.url.path.startswith(path) for path in self.PUBLIC_PATHS)
        
        if not is_public:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                from app.auth.jwt_handler import verify_token
                token = auth_header.split(" ")[1]
                payload = verify_token(token)
                if payload:
                    request.state.user = payload
        
        response = await call_next(request)
        return response