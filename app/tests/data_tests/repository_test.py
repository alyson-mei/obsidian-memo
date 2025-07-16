import pytest
import os
from sqlalchemy import inspect
from datetime import datetime

from app.data import database
from app.data.database_init import init_database
from app.data.repository import RepositoryFactory
from app.data.models import Bing

@pytest.mark.asyncio
async def test_repository():
    try:
        await init_database(database_url="sqlite+aiosqlite:///app/tests/data_tests/test.db")
        assert True
    except Exception as e:
        pytest.fail(f"Database initialization failed with error: {e}")
        return
    
    async with database.AsyncSessionLocal() as session:
        repo_factory = RepositoryFactory(session)
        bing_repo = repo_factory.get_repository(Bing)

        await bing_repo.truncate(max_entries=1, keep_entries=0)

        mock_data = {
            "image_url": "https://example.com/image.jpg",
            "title": "Test Image",
            "description": "A test description for the image",
            "date": "2025-07-15",
            "copyright": "TestCorp",
            "page_url": "https://example.com/page",
            "timestamp": datetime.now()
        }

        created_obj = await bing_repo.create(**mock_data)
        assert created_obj.title == "Test Image"
        assert created_obj.id is not None

        last_entry = await bing_repo.get_last()
        assert last_entry is not None
        assert last_entry.title == "Test Image"

        objs = [
            Bing(**{**mock_data, "title": "Second Image"}),
            Bing(**{**mock_data, "title": "Third Image"}),
        ]
        await bing_repo.create_many(objs)

        last_two = await bing_repo.get_last_n(2)
        assert len(last_two) == 2
        assert last_two[0].title == "Third Image"

        await bing_repo.delete_by_id(created_obj.id)
        deleted_check = await bing_repo.get_last_n(5)
        assert all(obj.id != created_obj.id for obj in deleted_check)

        await bing_repo.truncate(max_entries=1, keep_entries=1)
        entries = await bing_repo.get_last_n(5)
        assert len(entries) == 1

    os.remove("app/tests/data_tests/test.db")