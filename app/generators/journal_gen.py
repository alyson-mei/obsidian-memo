"""
journal_gen.py

This generator module creates creative journal and event entries for a character named Elizabeth (Liz)
in a cyberpunk setting. It leverages LLMs to generate realistic, contemplative, and original first-person
narratives and event vignettes, drawing on a rich character profile, recent entries, and curated examples.

Key features:
- Uses LLMs to generate both event and journal entries, each with distinct prompts and style guidelines.
- Incorporates character profile, signature items, rituals, and recent history to ensure continuity and depth.
- Avoids repetition and cliché by referencing recent entries and providing explicit negative examples.
- Enforces strict formatting, tone, and content rules to maintain narrative quality and authenticity.
- Saves generated entries to the database, managing table size with truncation.
- Provides robust logging and error handling throughout the process.

Typical usage:
- Invoked by scheduled jobs or user actions to keep a narrative journal up to date.
- Can be run as a standalone script for demonstration or creative inspiration.

Dependencies:
- app.services.llm (for LLM interaction), using pro model here
- app.data.database, app.data.repository, app.data.models (for DB operations)
- app.config (for configuration and logger setup)
"""

import asyncio
from typing import Literal

from app.services.llm import call_llm

from app.data.database_init import init_database
from app.data.repository import RepositoryFactory
from app.data.models import Journal
from app.data import database

from app.assets.prompts.journal_gen_prompts import (
    elizabeth_profile,
    events_examples,
    events_system_prompt,
    journal_system_prompt,
    event_human_prompt,
    journal_human_prompt
    )

from app.config import settings, setup_logger

NUM_LAST_JOURNAL_MSG = settings.num_last_journal_msg
MODEL_NAME_PRO = settings.model_name_pro

logger = setup_logger("journal_generator", indent=4)



async def get_recent_entries(entry: Literal['event', 'journal']) -> str:
    """Get recent commit messages, return empty string on failure."""
    try:
        async with database.AsyncSessionLocal() as session:
            repo = RepositoryFactory(session).get_repository(Journal)
            last_n_obj = await repo.get_last_n(n=NUM_LAST_JOURNAL_MSG)
            if entry == 'event':
                return "\n".join([obj.event for obj in last_n_obj])
            elif entry == 'journal':
                return "\n".join([obj.journal for obj in last_n_obj])
            else:
                raise Exception("Entry argument should be in ('event', 'journal')")
    except Exception as e:
        logger.warning(f"Failed to get recent entries: {e}")
        return ""

async def generate_journal_message():
    logger.info(f"Generating journal message")

    recent_events = await get_recent_entries(entry="event")
    recent_journals = await get_recent_entries(entry="journal")

    event_human_prompt_formatted = event_human_prompt.format(
        elizabeth_profile=elizabeth_profile,
        events_examples=events_examples,
        recent_events=recent_events
    )
    response_event = await call_llm(
        system_prompt=events_system_prompt,
        human_prompt=event_human_prompt_formatted,
        temperature=1.0,
        model=MODEL_NAME_PRO
        )

    journal_human_prompt_formatted = journal_human_prompt.format(
        elizabeth_profile=elizabeth_profile,
        response_event=response_event,
        recent_journals=recent_journals
    )

    response_journal = await call_llm(
        journal_system_prompt,
        journal_human_prompt_formatted,
        temperature=0.7,
        model=MODEL_NAME_PRO
        )
    
    logger.info(f"Saving journal message to database")
    try:
        async with database.AsyncSessionLocal() as session:
            repo = RepositoryFactory(session).get_repository(Journal)
            await repo.truncate(max_entries=20, keep_entries=10)
            await repo.create(
                event=response_event,
                journal=response_journal
            )
    except Exception as e:
        logger.error(f"Failed to save journal message: {e}")
    logger.info("Journal message saved to database.")
    
    return response_event, response_journal

async def main(update=True):
    await init_database()
    response_event, response_message = await generate_journal_message(update)
    print(response_event, '\n')
    print(response_message)

if __name__ == "__main__":
    asyncio.run(main())


