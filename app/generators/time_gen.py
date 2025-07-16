"""
time_gen.py

This generator module creates SVG progress bar charts visualizing the progress of various time periods
(day, week, month, season, year) based on the current local time. It generates both light and dark mode
SVGs, then saves them to the database for use in dashboards, journals, or other features.

Key features:
- Calculates time progress percentages for day, week, month, season, and year.
- Generates visually appealing horizontal bar charts in SVG format for both light and dark themes.
- Integrates with the database: saves new time progress messages and manages table size with truncation.
- Provides robust logging and error handling throughout the process.

Typical usage:
- Called by scheduled jobs or user actions to keep time progress visualizations up to date.
- Can be run as a standalone script for demonstration or testing.

Dependencies:
- matplotlib (for SVG chart generation)
- app.resources.styles (for fonts and color schemes)
- app.data.database, app.data.repository, app.data.models (for DB operations)
- app.config (for logger setup)
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from io import BytesIO

from app.assets.styles import POPPINS_REGULAR, TIME_PROGRESS_COLORS
from app.data.repository import RepositoryFactory
from app.data.models import Time
from app.data import database 
from app.config import setup_logger

logger = setup_logger("time_generator", indent=4)


async def generate_time_message(time_info: dict) -> None:
    """
    Generate SVG progress bar charts for time periods and save them to the database.

    Args:
        progress (dict): Dictionary with keys for 'day', 'week', 'month', 'season', 'year',
                         their percentage values, and a 'datetime' key.

    Returns:
        None
    """


    logger.info("Generating time message")

    prop = fm.FontProperties(fname=str(POPPINS_REGULAR))

    labels = [
        time_info["day"],
        time_info["week"],
        time_info["month"],
        time_info["season"],
        time_info["year"]
    ]
    values = [
        time_info["percentage_day"],
        time_info["percentage_week"],
        time_info["percentage_month"],
        time_info["percentage_season"],
        time_info["percentage_year"]
    ]
    
    colors = [TIME_PROGRESS_COLORS[key] for key in ['day', 'week', 'month', 'season', 'year']]

    def create_chart(text_color: str) -> str:
        """Create a horizontal bar chart SVG with the specified text color."""
        
        fig, ax = plt.subplots(figsize=(7, 3))
        fig.patch.set_facecolor("none")  # Transparent background
        ax.set_facecolor("none")         # Transparent background

        bars = ax.barh(labels, values, color=colors, edgecolor='none')

        # Remove all spines and ticks
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.xaxis.set_visible(False)
        ax.yaxis.set_ticks_position('none')
        ax.tick_params(left=False, labelleft=True)

        # Add percentage labels
        for bar, value in zip(bars, values):
            ax.text(value + 1, bar.get_y() + bar.get_height() / 2, f"{value:.2f}%",
                    va='center', ha='left', fontproperties=prop, fontsize=12, color=text_color)
            
        # Set y-axis labels with specified text color
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels, fontproperties=prop, fontsize=12, color=text_color)

        ax.set_xlim(0, 100)
        plt.tight_layout()

        # Save to buffer
        buf = BytesIO()
        plt.savefig(buf, format="svg", bbox_inches="tight", transparent=True)
        plt.close(fig)
        
        return buf.getvalue().decode("utf-8")

    # Generate both light and dark mode SVGs
    light_svg = create_chart(text_color="black")
    dark_svg = create_chart(text_color="white")

    # Save to database
    datetime = time_info["datetime"]
    logger.info(f"Saving time message to database")
    try:
        async with database.AsyncSessionLocal() as session:
            repo = RepositoryFactory(session).get_repository(Time)
            await repo.truncate(max_entries=12, keep_entries=4)
            await repo.create(
                message_light=light_svg,
                message_dark=dark_svg,
                date=datetime
            )
    except Exception as e:
        logger.error(f"Failed to save time message: {e}")
    logger.info("Time message saved to database.")

    return light_svg, dark_svg
