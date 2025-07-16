import pytest
import os

from app.data import database
from app.data.models import Bing
from app.data.database_init import init_database
from app.data.repository import RepositoryFactory
from app.generators.bing_gen import generate_bing_message

@pytest.mark.asyncio
async def test_generate_bing_message():
    await init_database(database_url="sqlite+aiosqlite:///app/tests/data_tests/test.db")
    response_content = await generate_bing_message()

    assert isinstance(response_content, dict)
    keys = ["image_url", "title", "description", "date", "copyright", "page_url"]
    
    for key in keys:
        assert key in keys, f"Field {key} is missing from the result"

    async with database.AsyncSessionLocal() as session:
        repo = RepositoryFactory(session).get_repository(Bing)
        last_entry = await repo.get_last()
        for key in keys:
            attr = getattr(last_entry, key)
            assert attr != ""
            print(attr)

    os.remove("app/tests/data_tests/test.db")
