import pytest

from app.data.db_init import init_db
from app.data.models import *

@pytest.mark.asyncio
async def test_init_db():
    try:
        await init_db()
        assert True
    except Exception as e:
        pytest.fail(f"Database initialization failed with error: {e}")