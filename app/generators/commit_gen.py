"""
commit_gen.py

This generator module creates unique, expressive commit messages for code repositories,
drawing inspiration from weather, time of day, mood, and creative references.
It leverages large language models (LLMs) to generate batches of commit messages that are
varied, emotionally rich, and often include cultural or atmospheric references.

Key features:
- Uses LLMs to generate batches of commit messages, with fallback to curated examples on failure.
- Ensures messages are unique, concise, and include relevant emojis.
- Incorporates recent commit history, weather data, and time of day to avoid repetition and add context.
- Provides robust logging and error handling throughout the generation and saving process.
- Saves generated commit messages to the database in efficient batches, managing table size.
- Includes a demonstration main function for testing and showcasing the generator.

Typical usage:
- Invoked as part of an automated workflow to generate commit messages for code pushes.
- Can be run interactively for inspiration or manual commit crafting.

Dependencies:
- app.services.llm (for LLM interaction)
- app.services.part_of_day (for contextual time-of-day info)
- app.data.database, app.data.repository, app.data.models (for DB operations)
- app.config (for configuration and logger setup)
- pydantic (for message schema validation)
"""

import random
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.services.llm import call_llm_structured
from app.services.time import get_part_of_day_description

from app.data import database
from app.data.repository import RepositoryFactory
from app.data.models import Commit

from app.assets.prompts.commit_gen_prompts import message_examples, system_prompt, human_prompt

from app.config import settings
from app.config import setup_logger


NUM_LAST_COMMIT_MSG = settings.num_last_commit_msg
NUM_NEW_COMMIT_MSG = settings.num_new_commit_msg
logger = setup_logger("commit_generator", indent=4)

class CommitMessage(BaseModel):
    message: str = Field(
        description="A concise, friendly commit message with emojis (max 10 words)"
    )

class CommitMessageBatch(BaseModel):
    messages: List[CommitMessage] = Field(
        description=f"List of {NUM_NEW_COMMIT_MSG} unique, creative commit messages",
        min_length=NUM_NEW_COMMIT_MSG,
        max_length=NUM_NEW_COMMIT_MSG * 2
    )

def get_default_commit_messages(count: int = NUM_NEW_COMMIT_MSG) -> List[str]:
    """Default factory: return random example messages when generation fails."""
    logger.info(f"Using default factory to get {count} commit messages")
    return random.sample(message_examples, min(count, len(message_examples)))

async def get_recent_commits() -> str:
    """Get recent commit messages, return empty string on failure."""
    try:
        async with database.AsyncSessionLocal() as session:
            repo = RepositoryFactory(session).get_repository(Commit)
            last_n_obj = await repo.get_last_n(n=NUM_LAST_COMMIT_MSG)
            return "\n".join([obj.message for obj in last_n_obj])
    except Exception as e:
        logger.warning(f"Failed to get recent commits: {e}")
        return ""

async def generate_commit_messages_batch(weather_data: dict, count: int = NUM_NEW_COMMIT_MSG) -> List[str]:
    """Generate commit messages using LLM, fallback to default on failure."""
    
    try:
        now = datetime.now()
        part_of_day = get_part_of_day_description(now.hour)
        last_n_msg = await get_recent_commits()
        
        logger.info(f"Generating {count} commit messages with LLM")
        
        example_messages = "\n".join([f"- {msg}" for msg in message_examples])
        
        system_prompt_formatted = system_prompt.format(
            num_last_commit_msg=last_n_msg,
            example_messages=example_messages,
            part_of_day=part_of_day,
            weather_data=weather_data,
            current_datetime=now.strftime('%Y-%m-%d %H:%M:%S'),
            last_n_msg=last_n_msg,
            count=count
        )

        human_prompt_formatted = human_prompt.format(count=count)

        response: Optional[CommitMessageBatch] = await call_llm_structured(
            system_prompt=system_prompt_formatted, 
            human_prompt=human_prompt_formatted, 
            response_model=CommitMessageBatch
        )
        
        if response and response.messages:
            messages = [msg.message for msg in response.messages]
            logger.info(f"Successfully generated {len(messages)} commit messages")
            return messages
        else:
            logger.warning("LLM returned empty response")
            return get_default_commit_messages(count)
            
    except Exception as e:
        logger.error(f"Failed to generate commit messages: {e}")
        return get_default_commit_messages(count)

async def save_commit_messages_batch(messages: List[str]) -> bool:
    """Save commit messages to database in a single batch."""
    if not messages:
        logger.warning("No messages to save")
        return False

    try:
        async with database.AsyncSessionLocal() as session:
            repo = RepositoryFactory(session).get_repository(Commit)
            await repo.truncate(max_entries=150, keep_entries=50)
            objs = [Commit(message=msg) for msg in messages]
            await repo.create_many(objs)
        logger.info(f"Successfully saved {len(messages)} commit messages (batch)")
        return True
    except Exception as e:
        logger.error(f"Failed to save commit messages: {e}")
        return False

async def generate_commit_messages(weather_data: dict, count: int = NUM_NEW_COMMIT_MSG) -> List[str]:
    """Generate and save commit messages. Always returns messages (uses default factory on failure)."""
    logger.info(f"Starting commit message generation and save process")
    
    messages = await generate_commit_messages_batch(weather_data, count)
    
    if messages:
        save_success = await save_commit_messages_batch(messages)
        if save_success:
            logger.info("Commit messages generated and saved successfully")
        else:
            logger.warning("Commit messages generated but failed to save")
    else:
        logger.error("No commit messages generated")
    
    return messages
