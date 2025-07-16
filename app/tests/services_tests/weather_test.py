import pytest

from app.services.weather import get_weather

@pytest.mark.asyncio
async def test_get_weather():
    weather_response = await get_weather()
    assert isinstance(weather_response, dict), "Weather response should be a dictionary"
    assert weather_response["error"] is None, f"Error occurred: {weather_response["error"]}"

    print("====== Weather ======")
    print(f"Weather Data: {weather_response["data"]}")
    print("====================", '\n')