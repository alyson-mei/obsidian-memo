from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings, setup_logger
from app.data import database  # Import the module, not individual items
import app.data.models # noqa: F401  # required for model discovery

DATABASE_URL = settings.database_url
logger = setup_logger("setup_database", indent=6)

async def init_database(database_url: str = DATABASE_URL, echo: bool = False):
    logger.info("Initializing database...")

    if database.engine and database.AsyncSessionLocal:
        logger.info("Database already initialized")
    else:
        try:
            database.engine = create_async_engine(url=database_url, echo=echo)

            database.AsyncSessionLocal = sessionmaker(
                autocommit=False, 
                autoflush=False, 
                expire_on_commit=False,
                class_=AsyncSession,
                bind=database.engine
                )

            async with database.engine.begin() as conn:
                await conn.run_sync(database.Base.metadata.create_all)
        
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise