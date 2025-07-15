import pytest
import asyncio
from pydantic import BaseModel

from app.services.llm import call_llm, call_llm_structured
from app.config import TIMEOUT, MODEL_NAME, MODEL_NAME_PRO

@pytest.mark.asyncio
@pytest.mark.parametrize("model", [MODEL_NAME, MODEL_NAME_PRO])
async def test_call_llm(model):
    tasks = [
        call_llm("You are helpful AI assistant", "What is Python?", model=model),
        call_llm("You are concise AI assistant", "Explain async/await in one sentence", model=model)
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)
    assert all(isinstance(result, str) for result in results), "All results should be strings"

    print(f"====== Basic LLM Calls ({model}) ======")
    for i, result in enumerate(results):
        print(f"Basic {i+1}: {result[:100]}..." if len(str(result)) > 100 else f"Basic {i+1}: {result}")
    print("==========================", '\n')

    await asyncio.sleep(3)
    
@pytest.mark.asyncio
@pytest.mark.parametrize("model", [MODEL_NAME, MODEL_NAME_PRO])
async def test_call_llm_structured(model):
        
    class TestResponse(BaseModel):
        topic: str
        points: list[str]

    class SummaryResponse(BaseModel):
        title: str = "Default Title"
        summary: str = "Default summary"

    tasks = [
    call_llm_structured(
        "List key points about the topic",
        "Machine learning basics",
        TestResponse,
        timeout=TIMEOUT,
        model=model
        ),
    call_llm_structured(
        "Summarize this topic",
        "Cloud computing advantages",
        SummaryResponse,
        timeout=TIMEOUT,
        model=model,
        default_factory=lambda: SummaryResponse(title="Fallback", summary="Could not summarize")
        )
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)
    assert all(isinstance(result, (TestResponse, SummaryResponse)) for result in results), "All results should be instances of the expected response models"
    
    print(f"====== Structured LLM Calls ({model}) ======")
    for i, result in enumerate(results):
        print(f"Structured {i+1}: {result}")
    print("==========================", '\n')

    await asyncio.sleep(3)