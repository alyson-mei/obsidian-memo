"""
db_init.py

Provides utilities for initializing the application's database schema using SQLAlchemy's async API.
This script can be run as a standalone module to create all tables defined in the app's models.

Key features:
- Imports all model definitions and the database engine.
- Defines an async init_db function to create all tables.
- Provides a main entry point for command-line initialization.
- Logs all steps and errors for observability.

Typical usage:
- Run directly to initialize or reset the database schema.
- Can be imported and called from other setup scripts.

Dependencies:
- app.data.models (for model/table definitions)
- app.data.database (for engine and Base)
- app.config (for logger setup)
"""

from app.data.database import Base, engine
from app.config import setup_logger

logger = setup_logger("init_database", indent=6)

async def init_db():
    logger.info("Initializing database")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

async def main():
    logger.info("Starting database initialization")
    await init_db()
    logger.info("Database initialization complete")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())