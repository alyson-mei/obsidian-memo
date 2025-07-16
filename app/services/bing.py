"""
bing.py

This module provides asynchronous utilities for fetching Bing's image of the day and its metadata
from the Peapix API, as well as scraping additional details (date, description) from the image's page.

- fetch_description_from_page: Scrapes a Bing image page for date and description using multiple strategies.
- get_peapix_image: Fetches Bing image metadata and enriches it with scraped details.
- main: Demonstrates usage and prints the fetched image metadata.

Logging is used throughout for observability. All network requests and parsing steps are robustly handled.
"""

import aiohttp
from typing import Dict
from bs4 import BeautifulSoup

from app.config import setup_logger

logger = setup_logger("bing_service", indent=6)

async def fetch_description_from_page(session, url: str) -> dict:
    """
    Fetch the date and description from a Bing image page.

    Args:
        session (aiohttp.ClientSession): The HTTP session to use.
        url (str): The URL of the page to fetch.

    Returns:
        dict: Dictionary with 'date' and 'description' if found, else empty.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/114.0.0.0 Safari/537.36"
    }
    try:
        logger.info(f"Fetching page: {url}...")
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

            result = {}

            # Multiple strategies for finding the date
            date_found = False
            
            # Strategy 1: Look for any <time> element - prefer text content over datetime attribute
            time_elem = soup.find("time")
            if time_elem and not date_found:
                # Try text content first (it's already formatted nicely)
                time_text = time_elem.get_text(strip=True)
                if time_text:
                    result["date"] = time_text
                    logger.info(f"Found date via time element text: {time_text}")
                    date_found = True
                else:
                    # Fallback to datetime attribute if no text
                    datetime_attr = time_elem.get("datetime")
                    if datetime_attr:
                        result["date"] = datetime_attr
                        logger.info(f"Found date via time element datetime: {datetime_attr}")
                        date_found = True

            # Strategy 2: Look for multiple time elements and choose the best one
            if not date_found:
                time_elements = soup.find_all("time")
                for time_elem in time_elements:
                    # Try text content first
                    time_text = time_elem.get_text(strip=True)
                    if time_text:
                        result["date"] = time_text
                        logger.info(f"Found date via multiple time search text: {time_text}")
                        date_found = True
                        break
                    # Fallback to datetime attribute
                    datetime_attr = time_elem.get("datetime")
                    if datetime_attr:
                        result["date"] = datetime_attr
                        logger.info(f"Found date via multiple time search datetime: {datetime_attr}")
                        date_found = True
                        break

            # Strategy 3: Look for date patterns in text content
            if not date_found:
                import re
                # Common date patterns
                date_patterns = [
                    r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
                    r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY or M/D/YYYY
                    r'\b\d{1,2}-\d{1,2}-\d{4}\b',  # MM-DD-YYYY
                    r'\b[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4}\b',  # Month DD, YYYY
                ]
                
                page_text = soup.get_text()
                for pattern in date_patterns:
                    match = re.search(pattern, page_text)
                    if match:
                        result["date"] = match.group()
                        logger.info(f"Found date via regex pattern: {match.group()}")
                        date_found = True
                        break

            # Strategy 4: Look for specific CSS selectors that might contain dates
            if not date_found:
                date_selectors = [
                    '[data-date]',
                    '.date',
                    '.publish-date',
                    '.created-date',
                    '[datetime]'
                ]
                
                for selector in date_selectors:
                    elem = soup.select_one(selector)
                    if elem:
                        date_value = (elem.get('data-date') or 
                                    elem.get('datetime') or 
                                    elem.get_text(strip=True))
                        if date_value:
                            result["date"] = date_value
                            logger.info(f"Found date via CSS selector {selector}: {date_value}")
                            date_found = True
                            break

            if not date_found:
                logger.info("Date element not found with any strategy.")

            # Description extraction (your original working logic)
            # Look for the position-relative container and combine all description paragraphs
            container = soup.find("div", class_="position-relative")
            if container:
                paragraphs = container.find_all("p")
                description_parts = []
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and not text.startswith("©") and len(text) > 10:
                        description_parts.append(text)
                if description_parts:
                    result["description"] = "\n\n".join(description_parts)
                    logger.info("Found description in position-relative container.")

            # Fallback: find all substantial paragraphs
            if "description" not in result:
                all_paragraphs = soup.find_all("p")
                description_parts = []
                for p in all_paragraphs:
                    text = p.get_text(strip=True)
                    if text and not text.startswith("©") and len(text) > 50:
                        description_parts.append(text)
                if description_parts:
                    result["description"] = "\n\n".join(description_parts)
                    logger.info("Found description in fallback paragraphs.")

            return result

    except Exception as e:
        logger.error(f"Error fetching description: {e}")
        return {}
    
async def get_peapix_data(country: str = "ca", count: int = 1) -> Dict[str, str]:
    """
    Fetch Bing image of the day and its metadata from Peapix.

    Args:
        country (str): Country code for the Bing image feed.
        count (int): Number of images to fetch.

    Returns:
        dict: Image metadata including url, title, description, date, copyright, and pageUrl.
    """
    url = f"https://peapix.com/bing/feed?country={country}&n={count}"
    headers = {"User-Agent": "Mozilla/5.0"}
    async with aiohttp.ClientSession() as session:
        try:
            logger.info(f"Fetching Peapix feed: {url}...")
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()

                image_data = data[0]
                page_url = image_data.get("pageUrl")
                logger.info(f"Image page URL: {page_url}")

                # Fetch page data asynchronously if page_url exists
                page_data = await fetch_description_from_page(session, page_url) if page_url else {}

                result = {
                    "image_url": image_data.get("fullUrl"),
                    "title": image_data.get("title"),
                    "description": page_data.get("description") if page_data else "(description not available)",
                    "date": page_data.get("date") if page_data else None,
                    "copyright": image_data.get("copyright"),
                    "page_url": page_url
                }
                logger.info("Fetched data successfully.")
                return {
                    "data": result,
                    "source": "primary",
                    "error": None
                }

        except Exception as e:
            logger.error(f"Request error: {e}")
            fallback = {
                "image_url": "",
                "title": "",
                "description": "",
                "date": "",
                "copyright": "",
                "page_url": ""
            }
            return {
                "data": fallback,
                "source": "fallback",
                "error": "No data from primary source"
            }
