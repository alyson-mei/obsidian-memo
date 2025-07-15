import pytest
from datetime import datetime

from app.services.time import (
    get_time_info, 
    get_part_of_day_description,
    get_season_range,
    get_days_in_month,
    get_start_of_next_year
)

def test_get_part_of_day_description():
    assert get_part_of_day_description(6) == "early morning"
    assert get_part_of_day_description(9) == "morning"
    assert get_part_of_day_description(12) == "noon"
    assert get_part_of_day_description(14) == "afternoon"
    assert get_part_of_day_description(17) == "early evening"
    assert get_part_of_day_description(19) == "evening"
    assert get_part_of_day_description(22) == "late evening"
    assert get_part_of_day_description(3) == "night"

    hour = datetime.now().hour
    print("====== Part of Day ======")
    print(f"Current hour: {hour}")
    print(f"Part of day: {get_part_of_day_description(hour)}")
    print("==========================", '\n')

def test_get_time_info():
    info = get_time_info()
    
    assert isinstance(info, dict)
    keys = [
        "day", 
        "month", 
        "week", 
        "season", 
        "year", 
        "datetime", 
        "percentage_day",
        "percentage_week",
        "percentage_month",
        "percentage_season",
        "percentage_year"
    ]
    for key in keys:
        assert key in info, f"Field {key} is missing from time info"

def test_current_time_info():
    """Test current time information display"""
    info = get_time_info()
    print("Current Time Information:")
    print(f"📅 {info['datetime']}")
    print(f"📊 Day: {info['percentage_day']:.1f}% complete")
    print(f"📊 Week: {info['percentage_week']:.1f}% complete") 
    print(f"📊 Month: {info['percentage_month']:.1f}% complete")
    print(f"📊 Season: {info['percentage_season']:.1f}% complete")
    print(f"📊 Year: {info['percentage_year']:.1f}% complete")

def test_new_years_day():
    """Test New Year's Day edge case"""
    test_date = datetime(2024, 1, 1, 0, 1)
    start_season, end_season = get_season_range(test_date)
    
    assert isinstance(start_season, datetime)
    assert isinstance(end_season, datetime)
    assert start_season <= test_date <= end_season

def test_leap_year_february_29():
    """Test leap year February 29th"""
    test_date = datetime(2024, 2, 29, 12, 0)
    days_in_month = get_days_in_month(2024, 2)
    
    assert days_in_month == 29
    assert test_date.month == 2
    assert test_date.day == 29

def test_non_leap_year_february():
    """Test non-leap year February"""
    feb_2023 = get_days_in_month(2023, 2)
    feb_2024 = get_days_in_month(2024, 2)
    
    assert feb_2023 == 28
    assert feb_2024 == 29

def test_december_31_end_of_year():
    """Test New Year's Eve (December 31st)"""
    test_date = datetime(2024, 12, 31, 23, 59)
    next_year_start = get_start_of_next_year(test_date)
    
    assert next_year_start.year == 2025
    assert next_year_start.month == 1
    assert next_year_start.day == 1

def test_season_transitions():
    """Test season transitions"""
    transitions = [
        datetime(2024, 2, 28, 23, 59),  # End of winter
        datetime(2024, 3, 1, 0, 0),     # Start of spring
        datetime(2024, 11, 30, 23, 59), # End of autumn
        datetime(2024, 12, 1, 0, 0),    # Start of winter
    ]
    
    for date in transitions:
        start_season, end_season = get_season_range(date)
        assert isinstance(start_season, datetime)
        assert isinstance(end_season, datetime)
        assert start_season <= end_season

def test_week_boundaries():
    """Test week boundaries (ISO weeks)"""
    test_dates = [
        datetime(2024, 6, 23, 23, 59),  # Sunday night
        datetime(2024, 6, 24, 0, 0),    # Monday morning
    ]
    
    for date in test_dates:
        iso_week = date.isocalendar()[1]
        assert isinstance(iso_week, int)
        assert 1 <= iso_week <= 53

def test_midnight_transitions():
    """Test midnight transitions"""
    midnight = datetime(2024, 6, 22, 0, 0)
    almost_midnight = datetime(2024, 6, 21, 23, 59)
    
    midnight_minutes = midnight.hour * 60 + midnight.minute
    almost_midnight_minutes = almost_midnight.hour * 60 + almost_midnight.minute
    
    assert midnight_minutes == 0
    assert almost_midnight_minutes == 1439  # 23*60 + 59

def test_month_length_variations():
    """Test month length variations"""
    months_to_test = [
        (2024, 1, 31),  # January - 31 days
        (2024, 2, 29),  # February - 29 days (leap)
        (2024, 4, 30),  # April - 30 days
        (2023, 2, 28),  # February - 28 days (non-leap)
    ]
    
    for year, month, expected_days in months_to_test:
        days = get_days_in_month(year, month)
        assert days == expected_days

def test_century_boundaries():
    """Test century/millennium boundaries"""
    century_dates = [
        datetime(1999, 12, 31, 23, 59),
        datetime(2000, 1, 1, 0, 0),
        datetime(2099, 12, 31, 23, 59),
        datetime(2100, 1, 1, 0, 0),
    ]
    
    for date in century_dates:
        next_year = get_start_of_next_year(date)
        assert next_year.year == date.year + 1

def test_invalid_month_handling():
    """Test error handling for invalid months"""
    with pytest.raises(ValueError):
        get_days_in_month(2024, 13)  # Invalid month
    
    with pytest.raises(ValueError):
        get_days_in_month(2024, 0)  # Invalid month