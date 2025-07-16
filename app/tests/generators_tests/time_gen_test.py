import pytest
import os

from app.data import database
from app.data.models import Time
from app.data.database_init import init_database
from app.data.repository import RepositoryFactory
from app.generators.time_gen import generate_time_message
from app.services.time import get_time_info

@pytest.mark.asyncio
async def test_generate_time_message():
    await init_database(database_url="sqlite+aiosqlite:///app/tests/data_tests/test.db")
    light_svg, dark_svg = await generate_time_message(get_time_info())

    assert all(isinstance(svg, str) for svg in (light_svg, dark_svg))
    for svg in (light_svg, dark_svg):
        assert len(svg) > 10

    keys = ["message_light", "message_dark", "date"]

    async with database.AsyncSessionLocal() as session:
        repo = RepositoryFactory(session).get_repository(Time)
        last_entry = await repo.get_last()
        for key in keys:
            attr = getattr(last_entry, key)
            assert attr != ""
            print(attr[:50])

    os.remove("app/tests/data_tests/test.db")