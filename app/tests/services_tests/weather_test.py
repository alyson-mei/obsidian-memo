import pytest

from app.services.weather import get_weather

@pytest.mark.asyncio
async def test_get_weather():
    weather_data = await get_weather()
    assert isinstance(weather_data, dict), "Weather data should be a dictionary"

    print("====== Weather ======")
    print(f"Weather Data: {weather_data}")
    print("====================", '\n')