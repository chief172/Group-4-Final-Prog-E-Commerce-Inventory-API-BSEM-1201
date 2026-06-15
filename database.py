"""
Database Configuration for Async PostgreSQL

This module provides:
- Async database engine with connection pooling
- Session factory for database operations
- Dependency injection for database sessions
- Startup and shutdown handlers
"""

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    AsyncEngine
)
from typing import AsyncGenerator
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Validate database URL
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set.\n"
        "Please create a .env file with: "
        "DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dbname"
    )

# Check if using async driver
if "asyncpg" not in DATABASE_URL:
    print("⚠️  WARNING: DATABASE_URL should use asyncpg driver")
    print(f"   Current: {DATABASE_URL}")
    print("   Expected format: postgresql+asyncpg://user:pass@localhost:5432/dbname")
    print("   Continuing anyway, but may cause errors...")

# ============================================================================
# ASYNC DATABASE ENGINE
# ============================================================================

def create_async_engine_with_config() -> AsyncEngine:
    """
    Create async database engine with optimal configuration.
    
    Returns:
        AsyncEngine: Configured async engine for PostgreSQL
    """
    return create_async_engine(
        DATABASE_URL,
        echo=True,  # Set to False in production to reduce logging
        future=True,  # Use SQLAlchemy 2.0 style
        pool_size=10,  # Maximum connections in pool
        max_overflow=20,  # Extra connections beyond pool_size
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=3600,  # Recycle connections after 1 hour
    )


# Create the async engine
engine = create_async_engine_with_config()

# ============================================================================
# ASYNC SESSION FACTORY
# ============================================================================

def create_async_session_factory():
    """
    Create async session factory for database operations.
    
    Returns:
        sessionmaker: Factory that creates AsyncSession instances
    """
    return sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,  # Don't expire objects after commit
        autocommit=False,  # Manual commit control
        autoflush=False,  # Manual flush control
    )


# Create the session factory
AsyncSessionLocal = create_async_session_factory()

# ============================================================================
# BASE MODEL CLASS
# ============================================================================

# Base class for all SQLAlchemy ORM models
Base = declarative_base()

# ============================================================================
# DEPENDENCY INJECTION FOR DATABASE SESSIONS
# ============================================================================

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injection for database sessions.
    
    This function is used with FastAPI's Depends() to provide
    database sessions to route handlers.
    
    Yields:
        AsyncSession: Database session for the request
        
    Example:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    
    Note:
        Session is automatically closed after the request completes.
        Rollback occurs automatically if an exception is raised.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# ============================================================================
# DATABASE INITIALIZATION AND CLEANUP
# ============================================================================

async def init_db() -> None:
    """
    Initialize the database by creating all tables.
    
    This should be called during application startup.
    Tables are created only if they don't already exist.
    
    Example:
        @app.on_event("startup")
        async def startup():
            await init_db()
    """
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created/verified")


async def close_db() -> None:
    """
    Close the database connection pool.
    
    This should be called during application shutdown.
    Ensures all connections are properly closed.
    
    Example:
        @app.on_event("shutdown")
        async def shutdown():
            await close_db()
    """
    await engine.dispose()
    print("✅ Database connection pool closed")


async def drop_db() -> None:
    """
    Drop all database tables.
    
    ⚠️ WARNING: This will delete all data!
    Use only for testing or resetting the database.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("⚠️  Database tables dropped")