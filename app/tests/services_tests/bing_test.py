import pytest

from app.services.bing import get_peapix_data

@pytest.mark.asyncio
async def test_get_peapix_data():
    peapix_response = await get_peapix_data()
    assert isinstance(peapix_response, dict), "Bing response should be a dictionary"
    assert peapix_response["error"] is None, f"Error occurred: {peapix_response["error"]}"

    data = peapix_response["data"]
    fields = ["image_url", "title", "description", "date", "copyright", "page_url"]
    for field in fields:
        assert field in data, f"Field {field} is missing from the result"

    print("====== Bing ======")
    print(f"Date: {data["date"]}")
    print(f"Title: {data["title"]}")
    print(f"Description: {data["description"]}")
    print(f"Image URL: {data["image_url"]}")
    print(f"Copyright: {data["copyright"]}")
    print(f"Page URL: {data["page_url"]}")
    print("==========================", '\n')

