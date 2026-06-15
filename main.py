"""
FastAPI Application Entry Point
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from typing import Dict, Any

from app.config.database import init_db, close_db
from app.config.settings import ENVIRONMENT, DEBUG, print_config_summary
from app.routes import (
    auth_router,
    user_router,
    category_router,
    product_router,
    cart_router,
    order_router,
    dashboard_router,
    admin_router
)
from app.middleware import (
    LoggingMiddleware,
    RateLimitMiddleware,
    RequestIDMiddleware,
    ErrorHandlerMiddleware
)


# ============================================================================
# LIFESPAN MANAGER
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    
    # --- STARTUP ---
    print("\n" + "=" * 60)
    print("🚀 STARTING E-COMMERCE INVENTORY API")
    print("=" * 60)
    print(f"Version:     {app.version}")
    print(f"Environment: {ENVIRONMENT}")
    print(f"Debug Mode:  {DEBUG}")
    print("=" * 60 + "\n")
    
    print_config_summary()
    
    print("\n📦 Initializing database...")
    await init_db()
    print("✅ Database ready")
    
    yield  # Application runs here
    
    # --- SHUTDOWN ---
    print("\n" + "=" * 60)
    print("🛑 SHUTTING DOWN API")
    print("=" * 60)
    await close_db()
    print("✅ Database disconnected")
    print("👋 Goodbye!\n")


# ============================================================================
# CREATE FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="E-Commerce Inventory API",
    description="Supporting SDG 8: Decent Work and Economic Growth in Sierra Leone",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)


# ============================================================================
# MIDDLEWARE CONFIGURATION (MUST BE AFTER app = FastAPI())
# ============================================================================

# 1. Error Handler - Catch all exceptions first
app.add_middleware(ErrorHandlerMiddleware)

# 2. Request ID - Add unique ID to each request
app.add_middleware(RequestIDMiddleware)

# 3. Logging - Log all requests and responses
app.add_middleware(LoggingMiddleware)

# 4. Rate Limiting - Prevent API abuse (60 requests per minute)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)

# 5. Trusted Host - Security against Host header attacks
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# 6. CORS - Allow frontend to connect (CRITICAL FOR FRONTEND)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# ============================================================================
# ROOT ENDPOINTS
# ============================================================================

@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """API Root Endpoint"""
    return {
        "name": "E-Commerce Inventory API",
        "version": "2.0.0",
        "status": "operational",
        "sdg": {
            "goal": "SDG 8 - Decent Work and Economic Growth",
            "location": "Sierra Leone",
            "impact": "Supporting local businesses with digital inventory management"
        },
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        "endpoints": {
            "auth": "/auth",
            "users": "/users",
            "categories": "/categories",
            "products": "/products",
            "cart": "/cart",
            "orders": "/orders",
            "dashboard": "/dashboard",
            "admin": "/admin"
        }
    }


@app.get("/health", tags=["Root"])
async def health_check() -> Dict[str, Any]:
    """Health Check Endpoint"""
    from datetime import datetime
    
    # Check database connection
    db_status = "unknown"
    try:
        from sqlalchemy import text
        from app.config.database import engine
        
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {str(e)[:50]}"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "environment": ENVIRONMENT,
        "components": {
            "api": "operational",
            "database": db_status
        }
    }


# ============================================================================
# REGISTER ROUTERS
# ============================================================================

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(category_router)
app.include_router(product_router)
app.include_router(cart_router)
app.include_router(order_router)
app.include_router(dashboard_router)
app.include_router(admin_router)


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    from fastapi.responses import JSONResponse
    from datetime import datetime
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "status_code": exc.status_code,
            "message": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unhandled exceptions"""
    from fastapi.responses import JSONResponse
    from datetime import datetime
    import logging
    
    logger = logging.getLogger(__name__)
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "status_code": 500,
            "message": "An internal server error occurred",
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )


# ============================================================================
# RUNNING THE APPLICATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=DEBUG,
        log_level="info"
    )