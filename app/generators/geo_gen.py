"""
geo_gen.py

This generator module creates engaging messages about the world's most breathtaking natural wonders.
It combines LLM-powered query generation, Tavily search results, and LLM-crafted descriptions to produce
a compelling narrative and select the best available images for each place.

Key features:
- Generates a unique, concise search query for a new natural wonder not previously used.
- Performs a Tavily search to gather text and image results about the selected place.
- Formats and summarizes search results, then prompts an LLM to write an inspiring, fact-based description.
- Selects and validates the best available images, prioritizing quality and relevance.
- Saves the generated message and image(s) to the database, managing table size with truncation.
- Provides robust logging and error handling throughout the process.

Typical usage:
- Invoked by scheduled jobs or user actions to enrich a feed of natural wonders.
- Can be run as a standalone script for demonstration or testing.

Dependencies:
- app.services.search (for Tavily search)
- app.services.llm (for LLM interaction), using pro model here
- app.data.database, app.data.repository, app.data.models (for DB operations)
- app.config (for configuration and logger setup)
- pydantic (for message schema validation)
"""

import asyncio, aiohttp
from pydantic import BaseModel, Field

from app.services.search import tavily_search
from app.services.llm import call_llm, call_llm_structured

from app.data import database
from app.data.models import Geo
from app.data.repository import RepositoryFactory

from app.assets.prompts.geo_gen_prompts import (
    search_system_prompt,
    message_system_prompt,
    search_human_prompt,
    message_human_prompt
)

from app.config import settings, setup_logger

NUM_LAST_SEARCH_MSG = settings.num_last_search_msg
MODEL_NAME_PRO = settings.model_name_pro
logger = setup_logger("geo_generator", indent=4)



class GeoMessage(BaseModel):
    place: str = Field(
        description="A chosen place"
    )
    message: str = Field(
        description="Engaging message about a beautiful place including interesting facts, geological features, etc."
    )
    image_url: list = Field(
        description="List with 1-5 URLs of images that best showcase the place's beauty and unique characteristics, sorted from more relevant to less relevant. You MUST include at least one image unless absolutely no images are related to the natural wonder.",
        min_length=1,
        max_length=5
    )

def default_geo_message() -> GeoMessage:
    """Factory function to create a default GeoMessage when LLM call fails"""
    return GeoMessage(
        place="Unknown Location",
        message="A beautiful natural wonder awaits discovery.",
        image_url=[""]  # Provide empty string instead of empty list to satisfy min_items=1
    )

def format_search_results_for_llm(search_results: dict) -> str:
    """
    Format search results in a clear, structured way for the LLM to process.
    
    Args:
        search_results (dict): Raw search results from Tavily
        
    Returns:
        str: Formatted string with clear sections for text content and images
    """
    formatted = []
    
    # Add query information
    if 'query' in search_results:
        formatted.append(f"Search Query: {search_results['query']}")
        formatted.append("")
    
    # Add answer if available
    if search_results.get('answer'):
        formatted.append("Answer Summary:")
        formatted.append(search_results['answer'])
        formatted.append("")
    
    # Add text results
    if 'results' in search_results and search_results['results']:
        formatted.append("Text Results:")
        for i, result in enumerate(search_results['results'], 1):
            formatted.append(f"{i}. Title: {result.get('title', 'N/A')}")
            formatted.append(f"   URL: {result.get('url', 'N/A')}")
            formatted.append(f"   Content: {result.get('content', 'N/A')}")
            formatted.append("")
    
    # Add images - This is the crucial part that was missing!
    if 'images' in search_results and search_results['images']:
        formatted.append("Available Images:")
        for i, image in enumerate(search_results['images'], 1):
            formatted.append(f"{i}. URL: {image.get('url', 'N/A')}")
            formatted.append(f"   Description: {image.get('description', 'N/A')}")
            formatted.append("")
    else:
        formatted.append("Available Images: None found")
        formatted.append("")
    
    return "\n".join(formatted)

async def check_image_availability(url: str, timeout: int = 10) -> bool:
    """
    Check if an image URL is accessible and returns a valid response.
    
    Args:
        url (str): The image URL to check
        timeout (int): Request timeout in seconds (default: 10)
    
    Returns:
        bool: True if image is accessible, False otherwise
    """
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.head(url) as response:
                # Check if status is successful and content-type indicates an image
                if response.status == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    return content_type.startswith('image/')
                return False
    except (aiohttp.ClientError, asyncio.TimeoutError, Exception):
        return False

async def get_first_available_image(image_urls: list) -> str:
    """
    Check each image URL in the list and return the first available one.
    
    Args:
        image_urls (list): List of image URLs to check
    
    Returns:
        str: First available image URL, or empty string if none are available
    """
    if not image_urls:
        return ""
    
    for url in image_urls:
        if await check_image_availability(url):
            return url
    
    return ""

async def get_available_images(image_urls: list, max_images: int = 3) -> list:
    """
    Check image URLs and return up to max_images available ones.
    
    Args:
        image_urls (list): List of image URLs to check
        max_images (int): Maximum number of images to return (default: 3)
    
    Returns:
        list: List of available image URLs (up to max_images)
    """
    if not image_urls:
        return []
    
    available_images = []
    for url in image_urls:
        if len(available_images) >= max_images:
            break
        if await check_image_availability(url):
            available_images.append(url)
    
    return available_images

async def generate_geo_message():
    """
    Generate a geo message about a natural wonder, save it to the database, and return the data.

    Returns:
        GeoMessage: Generated geo message with place, description, and available image URLs.
    """
    
    logger.info("Generating geo message")
    
    try:
        async with database.AsyncSessionLocal() as session:
            repo = RepositoryFactory(session).get_repository(Geo)
            last_n_obj = await repo.get_last_n(n=NUM_LAST_SEARCH_MSG)
            last_n_places = "\n".join([obj.place for obj in last_n_obj])
    except Exception as e:
        logger.error(f"Failed to fetch previous places: {e}")
        last_n_places = ""

    search_human_prompt_formatted = search_human_prompt.format(last_n_places=last_n_places)
    query = await call_llm(
        system_prompt=search_system_prompt,
        human_prompt=search_human_prompt_formatted,
        default_response="",
        model=MODEL_NAME_PRO
        )
    
    if not query:
        logger.error("Failed to generate search query")
        return default_geo_message()

    logger.info(f"Generated search query: {query}")
    
    try:
        # Use better search parameters
        search_results = await tavily_search(
            query, 
            max_results=8,
            topic="general",  # Use general topic as suggested
            include_images=True,
            include_image_descriptions=True,
            search_depth="basic",  # Try basic first, advanced might be too restrictive
            include_answer=True,  # Get answer for better context
            include_raw_content=False,
            time_range="month"  # Longer time range for better results
        )
        
        # Log the type and content of search_results for debugging
        logger.info(f"Search results type: {type(search_results)}")
        if isinstance(search_results, str):
            logger.warning(f"Search returned string instead of dict: {search_results[:200]}...")
        elif not search_results:
            logger.warning("Search returned empty results")
        else:
            logger.info(f"Search returned dict with keys: {search_results.keys() if isinstance(search_results, dict) else 'N/A'}")
            if isinstance(search_results, dict):
                num_results = len(search_results.get('results', []))
                num_images = len(search_results.get('images', []))
                logger.info(f"Found {num_results} text results and {num_images} images")
                
                # Log first few image URLs for debugging
                if search_results.get('images'):
                    for i, img in enumerate(search_results['images'][:3]):
                        logger.info(f"Image {i+1}: {img.get('url', 'No URL')}")
            
    except Exception as e:
        logger.error(f"Search failed: {e}")
        search_results = {}

    # Format the search results properly for the LLM
    formatted_results = format_search_results_for_llm(search_results)
    message_human_prompt_formatted = message_human_prompt.format(formatted_results=formatted_results)

    # Debug: Log the formatted results to see what's being sent to the LLM
    logger.debug(f"Formatted results for LLM:\n{formatted_results}")

    response = await call_llm_structured(
        message_system_prompt, 
        message_human_prompt, 
        response_model=GeoMessage,
        default_factory=default_geo_message,
        model=MODEL_NAME_PRO
    )

    # Debug: Log the raw response to see what the LLM returned
    logger.info(f"LLM response: {response}")

    if not response or not response.place or not response.message:
        logger.error("Failed to generate geo message")
        return default_geo_message()
    
    logger.info(f"Generated message for: {response.place}")
    logger.info(f"Initial image URLs: {response.image_url}")

    # Check image availability and get the first available one
    first_available_image = await get_first_available_image(response.image_url)
    
    logger.info(f"First available image: {first_available_image if first_available_image else 'None found'}")

    # Save to database
    logger.info("Saving geo message to database")
    try:
        async with database.AsyncSessionLocal() as session:
            repo = RepositoryFactory(session).get_repository(Geo)
            await repo.truncate(max_entries=150, keep_entries=50)
            await repo.create(
                place=response.place,
                message=response.message, 
                urls=first_available_image  # Save single URL string
            )
        logger.info("Geo message saved to database")
    except Exception as e:
        logger.error(f"Failed to save geo message: {e}")
    
    # Update response with the single available image for return
    response.image_url = [first_available_image] if first_available_image else []
    
    return response
