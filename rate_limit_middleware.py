"""
Rate Limiting Middleware - Limits requests per IP address
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
import time
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware to prevent API abuse"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_history = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for documentation
        public_paths = ["/docs", "/redoc", "/openapi.json", "/health"]
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)
        
        # Clean old entries
        current_time = time.time()
        self.request_history[client_ip] = [
            ts for ts in self.request_history[client_ip]
            if current_time - ts < 60
        ]
        
        # Check rate limit
        if len(self.request_history[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=429,
                detail=f"Too many requests. Limit: {self.requests_per_minute} requests per minute."
            )
        
        # Add current request
        self.request_history[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.requests_per_minute - len(self.request_history[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        
        return response