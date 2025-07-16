import pytest
import os

from app.data import database
from app.data.models import Geo
from app.data.database_init import init_database
from app.data.repository import RepositoryFactory

from app.generators.geo_gen import generate_geo_message

from app.config import settings

NUM_NEW_COMMIT_MSG = settings.num_new_commit_msg

@pytest.mark.asyncio
async def test_generate_geo_message():
    await init_database(database_url="sqlite+aiosqlite:///app/tests/data_tests/test.db")
    response_content = await generate_geo_message()
    
    assert response_content

    async with database.AsyncSessionLocal() as session:
        repo = RepositoryFactory(session).get_repository(Geo)
        last_entry = await repo.get_last()
        assert last_entry.message != ""
        print(last_entry.message)
    
    os.remove("app/tests/data_tests/test.db")
