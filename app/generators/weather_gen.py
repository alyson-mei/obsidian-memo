"""
weather_gen.py

This generator module creates human-friendly weather messages using large language models (LLMs).
It takes structured weather data and the current part of day, crafts a prompt, and uses an LLM to generate
a concise, expressive weather summary with a moody reflection. The result is saved to the database for use
in dashboards, journals, or other features.

Key features:
- Adapts output to the available weather data, omitting irrelevant or missing fields.
- Uses natural, interpretive language and emojis for clarity and emotional tone.
- Adds a short, introspective weather reflection tailored to the day's conditions.
- Integrates with the database: saves new weather messages and manages table size with truncation.
- Provides robust logging and error handling throughout the process.

Typical usage:
- Called by scheduled jobs or user actions to keep weather summaries up to date.
- Can be run as a standalone script for demonstration or testing.

Dependencies:
- app.services.llm (for LLM interaction)
- app.services.part_of_day (for contextual time-of-day info)
- app.data.database, app.data.repository, app.data.models (for DB operations)
- app.config (for configuration and logger setup)
"""

from datetime import datetime

from app.services.llm import call_llm
from app.services.time import get_part_of_day_description

from app.data.repository import RepositoryFactory
from app.data.models import Weather
from app.data import database

from app.assets.prompts.weather_gen_prompts import common_system_prompt, freeweather_example_prompt, tomorrowio_example_prompt

from app.config import settings, setup_logger

WEATHER_API = settings.weather_api
logger = setup_logger("weather_generator", indent=4)

prompt_selection = {"freeweather": freeweather_example_prompt, "tomorrow.io": tomorrowio_example_prompt}
hour = datetime.now().hour
part_of_day = get_part_of_day_description(hour)

system_prompt = common_system_prompt + prompt_selection[WEATHER_API]
human_prompt = "Weather data: \n {weather_data} \n Part of day: {part_of_day}"

async def generate_weather_message(weather_data: dict) -> str:
   """
   Generate a human-friendly weather message using LLM and save it to the database.

   Args:
      weather_data (dict): Structured weather data to be summarized.

   Returns:
      str: Generated weather message, or an error message if generation fails.
   """
   
   logger.info("Generating weather message")

   fhuman_prompt = human_prompt.format(
      weather_data=weather_data,
      part_of_day=part_of_day
      )
   
   response_content = await call_llm(system_prompt, fhuman_prompt, default_response="")

   if response_content == "":
      logger.error("Failed to generate weather message")
      return "Failed to generate weather message"
   
   logger.info(f"Saving weather message to database")
   try:
      async with database.AsyncSessionLocal() as session:
         repo = RepositoryFactory(session).get_repository(Weather)
         await repo.truncate(max_entries=128, keep_entries=64)
         await repo.create(message=response_content)
   except Exception as e:
        logger.error(f"Failed to save weather message: {e}")
   logger.info("Weather message saved to the database.")

   return response_content

async def main() -> None:
   from app.services.weather import get_weather
   weather_data = await get_weather()
   response_content = await generate_weather_message(weather_data)
   print(response_content)

if __name__ == '__main__':
   import asyncio
   asyncio.run(main())