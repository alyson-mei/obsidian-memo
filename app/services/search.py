"""
search.py

This module provides asynchronous utilities for performing web searches using the Tavily API.
It includes:

- tavily_search: Async function to perform a search with flexible parameters and robust error handling.
- main: Example usage and demonstration of the search function.

Logging is used throughout for observability. Configuration is handled via app.config.
The search function always returns a consistent dictionary structure, even on error.
"""

import asyncio
from typing import Any, Dict, Optional

from langchain_tavily import TavilySearch

from app.config import setup_logger

logger = setup_logger("search_service", indent=6)

async def tavily_search(
    query: str,
    max_results: int = 5,
    topic: str = "general",
    include_images: bool = True,
    include_image_descriptions: bool = True,
    search_depth: str = "basic",
    include_answer: bool = False,
    include_raw_content: bool = False,
    time_range: str = "day",
    include_domains: Optional[list] = None,
    exclude_domains: Optional[list] = None,
    timeout: int = 3,
    retries: int = 3
) -> Dict[str, Any]:
    """
    Perform a Tavily search with the given parameters.

    Args:
        query (str): The search query.
        max_results (int): Maximum number of results.
        topic (str): Topic for the search.
        include_images (bool): Whether to include images.
        include_image_descriptions (bool): Whether to include image descriptions.
        search_depth (str): Search depth ("basic" or "advanced").
        include_answer (bool): Whether to include an answer.
        include_raw_content (bool): Whether to include raw content.
        time_range (str): Time range for search results.
        include_domains (list, optional): Domains to include.
        exclude_domains (list, optional): Domains to exclude.
        timeout: Request timeout in seconds
        retries: Number of retry attempts

    Returns:
        dict: Search results in consistent dictionary format, empty dict if failed.
    """

    response = None
    
    for attempt in range(retries):
        try:
            logger.info(f"Starting Tavily search for query: '{query}'  (attempt) {attempt + 1}/{retries}")
            tool = TavilySearch(
                max_results=max_results,
                topic=topic,
                include_answer=include_answer,
                include_raw_content=include_raw_content,
                include_images=include_images,
                include_image_descriptions=include_image_descriptions,
                search_depth=search_depth,
                time_range=time_range,
                include_domains=include_domains,
                exclude_domains=exclude_domains,
                response_format="content"  # This returns a string by default
            )
            response = tool.invoke({"query": query})
            logger.info(f"Tavily search request completed, response type: {type(response)}")
            
            if response:
                response["query"] = query
                return {
                    "data": response,
                    "source": "primary",
                    "error": None
                }

        except Exception as e:
            logger.warning(f"Tavily search failed: {e}")
            
        if attempt < retries - 1:
            logger.info(f"Waiting {timeout}s before retry...")
            await asyncio.sleep(timeout)
            
    logger.error(f"Tavily search failed: {e}")
    
    fallback = {
        "query": query,
        "error": str(e),
        "results": [],
        "images": [],
        "answer": ""
    }
    return {
        "data": fallback,
        "source": "fallback",
        "error": "Critical error in search service"
    }
