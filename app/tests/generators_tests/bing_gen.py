import pytest

from app.generators.bing_gen import generate_bing_message

@pytest.mark.asyncio
async def test_generate_bing_message():
    response_content = await generate_bing_message()

    assert isinstance(response_content, dict)
    keys = ["image_url", "title", "description", "date", "copyright", "page_url"]
    
    for key in keys:
        assert key in keys, f"Field {key} is missing from the result"
