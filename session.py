"""
Database Session Management

This module provides utility functions for managing database sessions
outside of FastAPI's dependency injection system.
"""

from app.config.database import AsyncSessionLocal, engine


async def get_session():
    """
    Get an async database session directly.
    
    Use this for:
    - Background tasks
    - Scripts
    - Testing
    
    Usage:
        async with get_session() as db:
            result = await db.execute(select(User))
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db_session():
    """
    Initialize database session and create tables.
    
    Use this for standalone scripts or testing.
    """
    async with engine.begin() as conn:
        from database.base import Base
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables initialized")


async def close_db_session():
    """
    Close all database connections.
    
    Use this for cleanup in scripts.
    """
    await engine.dispose()
    print("✅ Database connections closed")