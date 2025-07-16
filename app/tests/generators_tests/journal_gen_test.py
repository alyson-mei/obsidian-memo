import pytest
import os

from app.data import database
from app.data.models import Journal
from app.data.database_init import init_database
from app.data.repository import RepositoryFactory

from app.generators.journal_gen import generate_journal_message

from app.config import settings

NUM_NEW_COMMIT_MSG = settings.num_new_commit_msg

@pytest.mark.asyncio
async def test_generate_journal_message():
    await init_database(database_url="sqlite+aiosqlite:///app/tests/data_tests/test.db")
    response_event, response_message = await generate_journal_message()

    for content in response_event, response_message:
        assert content != ""

    async with database.AsyncSessionLocal() as session:
        repo = RepositoryFactory(session).get_repository(Journal)
        last_entry = await repo.get_last()
        assert last_entry.event != ""
        assert last_entry.journal != ""
        print(last_entry.event)
        print(last_entry.journal)

    os.remove("app/tests/data_tests/test.db")
