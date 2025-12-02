"""Dependency injection utilities."""


async def get_db():
    """Get database instance.

    This dependency ensures db is initialized before use.
    Lazy-imports to avoid NoneType issues during module initialization.
    """
    from app.db import db

    if db is None:
        raise RuntimeError("Database not initialized. Check startup events.")
    return db
