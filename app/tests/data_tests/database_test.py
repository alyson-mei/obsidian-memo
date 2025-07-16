import pytest
import os
from sqlalchemy import inspect

from app.data import database
from app.data.database_init import init_database

@pytest.mark.asyncio
async def test_init_db():
    try:
        await init_database(database_url="sqlite+aiosqlite:///app/tests/data_tests/test.db")
        assert True
    except Exception as e:
        pytest.fail(f"Database initialization failed with error: {e}")

    async with database.engine.begin() as conn:
        def get_tables(connection):
            inspector = inspect(connection)
            return set(inspector.get_table_names())
        
        existing_tables = await conn.run_sync(get_tables)
    
    expected_tables = {"bing", "commit", "geo", "journal", "time", "weather"}

    print(f"====== Database ======")
    print(existing_tables, expected_tables)
    print("==========================", '\n')

    assert expected_tables.issubset(existing_tables), (
        f"Some models' tables are missing: {expected_tables - existing_tables}"
    )
    assert database.AsyncSessionLocal

    os.remove("app/tests/data_tests/test.db")