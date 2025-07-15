import pytest

from app.services.search import tavily_search

@pytest.mark.asyncio
async def test_tavily_search():
    query = "An interesting fact about some beautiful place in the world"
    response = await tavily_search(query)
    
    assert isinstance(response, dict)
    assert response["query"] 
    assert response["results"] 
    assert response["images"]

    print("====== Tavily Search ======")
    print(f"Query: {response["query"]}")
    print(f"Results: {response["results"]}")
    print(f"Images: {response["images"]}")
    print("==========================", '\n')
