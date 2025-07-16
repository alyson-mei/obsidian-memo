"""
llm.py

This module provides asynchronous utilities for interacting with large language models (LLMs)
using the LangChain framework. It includes:

- call_llm: Async function to get a basic text response from an LLM with timeout, logging, and fallback.
- call_llm_structured: Async function to get a structured (Pydantic-validated) response from an LLM,
  with timeout, logging, and fallback/default handling.
- main: Demonstrates usage and tests both basic and structured LLM calls.

Logging is used throughout for observability. Configuration is handled via app.config.
Timeouts and error handling ensure robust operation and predictable fallbacks.
"""

import asyncio, re, time
from typing import TypeVar, Type, Optional
from pydantic import BaseModel

from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage

from app.config import settings, setup_logger

logger = setup_logger("llm_service", indent=6)
MODEL_NAME = settings.model_name
MODEL_PROVIDER = settings.model_provider
DEFAULT_RESPONSE = settings.default_response
TIMEOUT = settings.timeout

async def call_llm(
        system_prompt: str,
        human_prompt: str,
        model: str = MODEL_NAME,
        model_provider: str = MODEL_PROVIDER,
        temperature: float = 0.7,
        timeout: int = TIMEOUT,
        default_response: str = DEFAULT_RESPONSE
        ) -> str:
    """
    Call LLM with basic text response.
    
    Args:
        system_prompt: System message for the LLM
        human_prompt: User message for the LLM
        model: Model name to use
        model_provider: Provider for the model
        temperature: Sampling temperature
        timeout: Request timeout in seconds
        default_response: Fallback response if request fails
        
    Returns:
        LLM response or default_response on failure
    """
    start_time = time.time()
    
    try:
        logger.info(f"Calling LLM: {model_provider}/{model}")
        
        llm = init_chat_model(
            model=model,
            model_provider=model_provider,
            temperature=temperature,
            timeout=timeout
        )
        
        # Manual timeout check with asyncio
        response = await asyncio.wait_for(
            llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]),
            timeout=timeout
        )
        
        elapsed = time.time() - start_time
        logger.info(f"LLM call completed in {elapsed:.2f}s")
        
        if response.content:
            return {
                "data": response.content.strip(),
                "source": "primary",
                "error": None
            }
        else: 
            return {
                "data": default_response,
                "source": "default_response",
                "error": "No data from primary source"
            }
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"LLM call failed after {elapsed:.2f}s: {e}")
        return {
            "data": default_response,
            "source": "default_response",
            "error": e
        }


T = TypeVar('T', bound=BaseModel)

async def call_llm_structured(
        system_prompt: str,
        human_prompt: str,
        response_model: Type[T],
        model: str = MODEL_NAME,
        model_provider: str = MODEL_PROVIDER,
        temperature: float = 0.7,
        timeout: int = TIMEOUT,
        default_factory: Optional[callable] = None
        ) -> Optional[T]:
    """
    Call LLM with structured Pydantic response.
    
    Args:
        system_prompt: System message for the LLM
        human_prompt: User message for the LLM
        response_model: Pydantic model class for response validation
        model: Model name to use
        model_provider: Provider for the model
        temperature: Sampling temperature
        timeout: Request timeout in seconds
        default_factory: Optional callable that returns default instance of response_model
        
    Returns:
        Validated Pydantic model instance, default instance, or None on failure
    """
    start_time = time.time()
    
    try:
        logger.info(f"Calling structured LLM: {model_provider}/{model}")
        
        enhanced_prompt = (
            f"{system_prompt}\n\n"
            f"Respond ONLY with JSON — no explanations, no markdown, no extra text. "
            f"Use the following JSON schema: {response_model.model_json_schema()}"
        )
        
        llm = init_chat_model(
            model=model, 
            model_provider=model_provider, 
            temperature=temperature, 
            timeout=timeout
        )
        
        # Manual timeout check with asyncio
        response = await asyncio.wait_for(
            llm.ainvoke([
                SystemMessage(content=enhanced_prompt), 
                HumanMessage(content=human_prompt)
            ]),
            timeout=timeout
        )
        
        elapsed = time.time() - start_time
        logger.info(f"Structured LLM call completed in {elapsed:.2f}s")
        
        content = response.content.strip() if response.content else ""
        
        # Extract JSON from markdown if needed
        if content.startswith('```'):
            json_match = re.search(r'```(?:json)?\n?(.*?)\n?```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1).strip()
        
        if not content:
            raise ValueError("Empty response content")
            
        result = response_model.model_validate_json(content)
        logger.debug(f"Successfully parsed structured response: {type(result).__name__}")
        return {
            "data": result,
            "source": "primary",
            "error": None
        }        
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Structured LLM call failed after {elapsed:.2f}s: {e}")
        return {
            "data": default_factory() if default_factory else None,
            "source": "default_factory",
            "error": "No data from primary source"
        } 
