import pytest

from app.services.search import tavily_search

@pytest.mark.asyncio
async def test_tavily_search():
    query = "An interesting fact about some beautiful place in the world"
    search_response = await tavily_search(query)
    
    assert isinstance(search_response, dict), "Search response should be a dictionary"
    assert search_response["error"] is None, f"Error occurred: {search_response["error"]}"
    
    data = search_response["data"]
    print("====== Tavily Search ======")
    print(f"Query: {data["query"]}")
    print(f"Results: {data["results"]}")
    print(f"Images: {data["images"]}")
    print("==========================", '\n')
