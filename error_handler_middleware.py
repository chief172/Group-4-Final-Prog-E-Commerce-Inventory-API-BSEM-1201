"""
Error Handler Middleware - Catches and processes all exceptions
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
import logging
import traceback
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
            
        except HTTPException as http_exc:
            logger.warning(f"HTTP {http_exc.status_code}: {http_exc.detail}")
            return JSONResponse(
                status_code=http_exc.status_code,
                content={
                    "success": False,
                    "status_code": http_exc.status_code,
                    "message": http_exc.detail,
                    "path": request.url.path,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
            
        except Exception as exc:
            logger.error(f"Unhandled exception: {str(exc)}\n{traceback.format_exc()}")
            return JSONResponse(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "status_code": 500,
                    "message": "An internal server error occurred",
                    "path": request.url.path,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )