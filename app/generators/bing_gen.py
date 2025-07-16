"""
bing_gen.py

This generator module is responsible for creating Bing image messages for the application.
It fetches the Bing image of the day and its metadata (such as title, description, date, and copyright)
from the Peapix API using the async service layer. The generator then saves the resulting image data
to the database for later use in dashboards, journals, or other features.

Key features:
- Asynchronous fetching of Bing image metadata and description.
- Robust logging for each step of the process, including error handling.
- Database integration: saves new Bing image messages and manages table size with truncation.
- Returns a dictionary with all relevant Bing image data, even if fetching or saving fails.

Typical usage:
- Called by scheduled jobs or user actions to keep the Bing image feed up to date.
- Can be run as a standalone script for testing or demonstration.

Dependencies:
- app.services.bing (for Peapix API access)
- app.data.database, app.data.repository, app.data.models (for DB operations)
- app.config (for logger setup)
"""

from app.services.bing import get_peapix_data
from app.data import database
from app.data.repository import RepositoryFactory
from app.data.models import Bing
from app.config import setup_logger

logger = setup_logger("bing_generator", indent=4)

async def generate_bing_message(country: str = "ca", count: int = 1) -> dict:
    """
    Generate a Bing image message, save it to the database, and return the image data.

    Args:
        country (str): Country code for the Bing image feed (default: "ca").
        count (int): Number of images to fetch (default: 1).

    Returns:
        dict: Dictionary containing Bing image metadata and description.
    """
    
    logger.info("Generating Bing message")
    bing_data = await get_peapix_data(country, count)
    
    if bing_data and bing_data["image_url"] != "" and bing_data["title"] != "":
        logger.info("Saving Bing message to database")
        try:
            async with database.AsyncSessionLocal() as session:
                repo = RepositoryFactory(session).get_repository(Bing)
                await repo.truncate(max_entries=12, keep_entries=4)
                await repo.create(
                    image_url=bing_data.get("image_url"),
                    title=bing_data.get("title"),
                    description=bing_data.get("description"),
                    date=bing_data.get("date"),
                    copyright=bing_data.get("copyright"),
                    page_url=bing_data.get("page_url"),
                )
        except Exception as e:
            logger.error(f"Failed to save Bing message: {e}")
        logger.info(f"Bing message saved to the database")
    else:
        logger.error(f"Failed to generate Bing message")
    
    return bing_data