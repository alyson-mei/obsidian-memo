"""
time.py

This module provides utilities for calculating and describing time progress
across various periods (day, week, month, season, year). It includes:

- get_days_in_month: Returns the number of days in a given month/year.
- get_season_range: Determines the start and end dates of the current meteorological season.
- get_start_of_next_year: Returns a datetime for the start of the next year.
- get_time_info: Calculates progress percentages and labels for day, week, month, season, and year.

Logging is used for observability. All calculations use the current local time.
Includes an extensive __main__ section for edge case testing and demonstration.
"""

import calendar
from datetime import datetime, timedelta
from typing import Dict, Tuple, Union

from app.config import setup_logger

logger = setup_logger("time_service", indent=6)

def get_part_of_day_description(hour: int) -> str:
    """
    Return a human-readable description for the part of day based on the hour.

    Args:
        hour (int): The hour of the day (0-23).

    Returns:
        str: Description of the part of day.
    """
    logger.info(f"Getting part of day description for hour: {hour}")
    if 5 <= hour < 8:
        return "early morning"
    elif 8 <= hour < 12:
        return "morning"
    elif 12 <= hour < 13:
        return "noon"
    elif 13 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 18:
        return "early evening"
    elif 18 <= hour < 21:
        return "evening"
    elif 21 <= hour < 23:
        return "late evening"
    else:
        return "night"

def get_days_in_month(year: int, month: int) -> int:
    """
    Get the number of days in a given month of a given year.
    
    Args:
        year: The year (e.g., 2024)
        month: The month (1-12)
    
    Returns:
        The number of days in the specified month
        
    Raises:
        ValueError: If month is not in range 1-12
        
    Examples:
        >>> get_days_in_month(2024, 2)  # Leap year February
        29
        >>> get_days_in_month(2023, 2)  # Non-leap year February  
        28
        >>> get_days_in_month(2023, 4)  # April
        30
    """
    if not 1 <= month <= 12:
        raise ValueError(f"Month must be between 1 and 12, got {month}")
    
    return calendar.monthrange(year, month)[1]


def get_season_range(now: datetime) -> Tuple[datetime, datetime]:
    """
    Get the start and end dates of the current season.
    
    Seasons are defined as:
    - Winter: December 1 - February 28/29
    - Spring: March 1 - May 31
    - Summer: June 1 - August 31
    - Autumn: September 1 - November 30
    
    Args:
        now: The current date and time
    
    Returns:
        A tuple containing (season_start, season_end) as datetime objects
        
    Examples:
        >>> import datetime
        >>> get_season_range(datetime.datetime(2024, 1, 15))
        (datetime.datetime(2023, 12, 1, 0, 0), datetime.datetime(2024, 3, 1, 0, 0))
        >>> get_season_range(datetime.datetime(2024, 7, 15))
        (datetime.datetime(2024, 6, 1, 0, 0), datetime.datetime(2024, 9, 1, 0, 0))
    """
    season_start_month = (
        12 if now.month in [12, 1, 2] else
        3 if now.month in [3, 4, 5] else
        6 if now.month in [6, 7, 8] else
        9
    )
    
    # Handle year transition for winter
    if season_start_month == 12:
        season_start = now.replace(month=12, day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month in [1, 2]:  # We're in Jan/Feb, so winter started last year
            season_start = season_start.replace(year=now.year - 1)
        season_end = now.replace(year=season_start.year + 1, month=3, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        season_start = now.replace(month=season_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
        season_end = season_start.replace(month=season_start_month + 3, day=1)
    
    return season_start, season_end


def get_start_of_next_year(now: datetime) -> datetime:
    """
    Get the start of the next year (January 1st at midnight).
    
    Args:
        now: The current date and time
    
    Returns:
        A datetime object representing January 1st at 00:00:00 of the next year
        
    Examples:
        >>> import datetime
        >>> get_start_of_next_year(datetime.datetime(2024, 6, 15, 14, 30))
        datetime.datetime(2025, 1, 1, 0, 0)
    """
    return now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)


def get_time_info() -> Dict[str, Union[str, float]]:
    """
    Calculate the progress of the current day, week, month, season, and year.
    
    This function computes how much of each time period has elapsed as a percentage,
    along with descriptive labels for the current time periods.
    
    Returns:
        A dictionary containing:
        - day: Day name (e.g., "Monday")
        - month: Month name (e.g., "January") 
        - week: Week description (e.g., "Week 25")
        - season: Season name ("Winter", "Spring", "Summer", or "Autumn")
        - year: Year description (e.g., "Year 2024")
        - datetime: Formatted current datetime string
        - percentage_day: Percentage of current day completed (0.0-100.0)
        - percentage_week: Percentage of current week completed (0.0-100.0)
        - percentage_month: Percentage of current month completed (0.0-100.0)
        - percentage_season: Percentage of current season completed (0.0-100.0)
        - percentage_year: Percentage of current year completed (0.0-100.0)
        
    Examples:
        >>> info = get_time_info()
        >>> print(f"Today is {info['day']} and we're {info['percentage_day']:.1f}% through the day")
        Today is Sunday and we're 45.2% through the day
        
    Note:
        - Week starts on Monday (ISO 8601 standard)
        - Seasons are meteorological (Dec-Feb, Mar-May, Jun-Aug, Sep-Nov)
        - All percentages are calculated based on elapsed minutes
    """
    logger.info("Calculating time progress percentages")
    now = datetime.now()
    day = now.strftime("%A")
    month = now.strftime("%B")
    week = f"Week {now.isocalendar()[1]}"
    season = (
        "Winter" if now.month in [12, 1, 2] else
        "Spring" if now.month in [3, 4, 5] else
        "Summer" if now.month in [6, 7, 8] else
        "Autumn"
    )

    # Day progress
    minutes_today = now.hour * 60 + now.minute
    percentage_day = (minutes_today / (24 * 60)) * 100

    # Week progress (ISO week starting Monday)
    start_of_week = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=now.weekday())
    minutes_since_start = int((now - start_of_week).total_seconds() // 60)
    percentage_week = (minutes_since_start / (7 * 24 * 60)) * 100

    # Month progress
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    minutes_this_month = int((now - start_of_month).total_seconds() // 60)
    days_in_month = get_days_in_month(now.year, now.month)
    percentage_month = (minutes_this_month / (days_in_month * 24 * 60)) * 100

    # Season progress
    start_of_season, end_of_season = get_season_range(now)
    minutes_this_season = int((now - start_of_season).total_seconds() // 60)
    total_minutes_in_season = int((end_of_season - start_of_season).total_seconds() // 60)
    percentage_season = (minutes_this_season / total_minutes_in_season) * 100

    # Year progress
    year = f"Year {now.year}"
    start_of_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_year = get_start_of_next_year(now)
    minutes_this_year = int((now - start_of_year).total_seconds() // 60)
    total_minutes_in_year = int((end_of_year - start_of_year).total_seconds() // 60)
    percentage_year = (minutes_this_year / total_minutes_in_year) * 100

    logger.info("Completed calculations")

    return {
        "day": day,
        "month": month,
        "week": week,
        "season": season,
        "year": year,
        "datetime": now.strftime("%A, %d %B %Y | %H:%M"),
        "percentage_day": percentage_day,
        "percentage_week": percentage_week,
        "percentage_month": percentage_month,
        "percentage_season": percentage_season,
        "percentage_year": percentage_year,
    }

