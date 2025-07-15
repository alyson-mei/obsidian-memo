import pytest

from app.services.bing import get_peapix_data

@pytest.mark.asyncio
async def test_get_peapix_data():
    result = await get_peapix_data()

    assert isinstance(result, dict)

    fields = ["image_url", "title", "description", "date", "copyright", "page_url"]
    for field in fields:
        assert field in result, f"Field {field} is missing from the result"

    print("====== Bing ======")
    print(f"Date: {result["date"]}")
    print(f"Title: {result["title"]}")
    print(f"Description: {result["description"]}")
    print(f"Image URL: {result["image_url"]}")
    print(f"Copyright: {result["copyright"]}")
    print(f"Page URL: {result["page_url"]}")
    print("==========================", '\n')

