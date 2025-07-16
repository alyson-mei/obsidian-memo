import pytest
import os

from app.data import database
from app.data.models import Weather
from app.data.database_init import init_database
from app.data.repository import RepositoryFactory

from app.services.weather import get_weather
from app.generators.weather_gen import generate_weather_message

from app.config import settings

NUM_NEW_COMMIT_MSG = settings.num_new_commit_msg

@pytest.mark.asyncio
async def test_generate_weather_message():
    await init_database(database_url="sqlite+aiosqlite:///app/tests/data_tests/test.db")
    weather_data = await get_weather()
    response_content = await generate_weather_message(weather_data)
    
    assert response_content

    async with database.AsyncSessionLocal() as session:
        repo = RepositoryFactory(session).get_repository(Weather)
        last_entry = await repo.get_last()
        assert last_entry.message != ""
        print(last_entry.message)
    
    os.remove("app/tests/data_tests/test.db")

