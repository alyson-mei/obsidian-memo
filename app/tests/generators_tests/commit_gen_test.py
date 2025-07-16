import pytest
import os

from app.data import database
from app.data.models import Commit
from app.data.database_init import init_database
from app.data.repository import RepositoryFactory

from app.services.weather import get_weather
from app.generators.commit_gen import generate_commit_messages

from app.config import settings

NUM_NEW_COMMIT_MSG = settings.num_new_commit_msg

@pytest.mark.asyncio
async def test_generate_commit_message():
    await init_database(database_url="sqlite+aiosqlite:///app/tests/data_tests/test.db")
    weather_data = await get_weather()
    messages = await generate_commit_messages(weather_data)

    assert messages

    async with database.AsyncSessionLocal() as session:
        repo = RepositoryFactory(session).get_repository(Commit)
        last_entries = await repo.get_last_n(n=NUM_NEW_COMMIT_MSG)
        print(msg.message for msg in last_entries)

    os.remove("app/tests/data_tests/test.db")
