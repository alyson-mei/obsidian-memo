"""
ui_state.py

This module defines the UIState class, which manages the loading, aggregation, and presentation
of application state for the user interface layer. It coordinates fetching the latest data from
the database (commits, Bing images, weather, time progress, geo wonders, and journal entries),
formats this data for display, and renders output files such as the README and SVG resources.

Key features:
- Asynchronously loads all relevant data from the database using repository patterns.
- Aggregates and formats state for use in UI templates and resource files.
- Provides robust logging and error handling for each data source.
- Supports rendering the main README and writing resource files for the UI.
- Offers a single update_ui method to refresh all UI outputs in one step.
- Maintains error state to track and report any issues during data loading or rendering.

Typical usage:
- Instantiated as a singleton (state) and called by UI update routines or scheduled jobs.
- Used to keep the UI in sync with the latest generated and stored data.

Dependencies:
- app.data.repository, app.data.models, app.data.database (for DB operations)
- app.config (for configuration, paths, and logger setup)
- Python standard library (datetime, typing)
"""

from datetime import datetime, timedelta
from typing import Dict, List

from app.data.repository import RepositoryFactory
from app.data.models import Commit, Journal, Weather, Time, Bing, Geo
from app.data import database 
from app.config import UI_DIR, TEMPLATES_DIR, NUM_NEW_COMMIT_MSG, JOURNAL_MESSAGE_HOUR
from app.config import setup_logger

logger = setup_logger("ui", indent=2)

class UIState:
    def __init__(self, num_messages: int = NUM_NEW_COMMIT_MSG):
        self.num_messages = num_messages
        self.has_errors = False
        
        # Initialize with defaults
        self.commit_messages: List[str] = []
        self.bing_data: Dict[str, str] = {}
        self.weather_msg = "{weather_msg}"  # Keep placeholder for template
        self.time_msg_light = "-"
        self.time_msg_dark = "-"
        self.geo_place = "-"
        self.geo_msg = "-"
        self.geo_url = ""
        self.journal_msg = ""
        
        # Generated properties
        now = datetime.now()
        self.timestamp = int(now.timestamp())
        self.datetime = now.strftime("%A, %d %B %Y | %H:%M").lower()
        self.date = now.strftime("%d %b %Y").lower()
        self.commit_msg = f"No commits available - {now}"

    async def _load_commits(self, repo_factory: RepositoryFactory) -> None:
        """Load commit messages from database only if not already loaded."""
        if self.commit_messages:
            # Already have commit messages, use the most recent one
            self.commit_msg = self.commit_messages.pop()
            return
            
        try:
            commit_repo = repo_factory.get_repository(Commit)
            
            if commit_repo:
                recent_commits = await commit_repo.get_last_n(n=self.num_messages)
                self.commit_messages = [msg.message for msg in recent_commits]
                if self.commit_messages:
                    self.commit_msg = self.commit_messages.pop()  # Use most recent
            else:
                logger.error("Failed to load commit repository")
                self.has_errors = True
        except Exception as e:
            logger.error(f"Error loading commits: {e}")
            self.has_errors = True

    async def _load_bing_data(self, repo_factory: RepositoryFactory) -> None:
        """Load Bing data from database."""
        try:
            bing_repo = repo_factory.get_repository(Bing)
            bing_record = await bing_repo.get_last()
            if bing_record:
                self.bing_data = {
                    "url": bing_record.url,
                    "title": bing_record.title,
                    "description": bing_record.description,
                    "page_date": bing_record.page_date,
                    "copyright": bing_record.copyright,
                    "page_url": bing_record.page_url
                }
            else:
                logger.error("No Bing data found")
                self.has_errors = True
        except Exception as e:
            logger.error(f"Error loading Bing data: {e}")
            self.has_errors = True

    async def _load_weather(self, repo_factory: RepositoryFactory) -> None:
        """Load weather data from database."""
        try:
            weather_repo = repo_factory.get_repository(Weather)
            weather_record = await weather_repo.get_last()
            if weather_record:
                self.weather_msg = weather_record.message
            else:
                logger.error("No weather data found")
                self.has_errors = True
        except Exception as e:
            logger.error(f"Error loading weather data: {e}")
            self.has_errors = True

    async def _load_time_data(self, repo_factory: RepositoryFactory) -> None:
        """Load time-related data from database."""
        try:
            time_repo = repo_factory.get_repository(Time)
            time_record = await time_repo.get_last()
            if time_record:
                self.time_msg_light = time_record.message_light
                self.time_msg_dark = time_record.message_dark
            else:
                logger.error("No time data found")
                self.has_errors = True
        except Exception as e:
            logger.error(f"Error loading time data: {e}")
            self.has_errors = True

    async def _load_geo_data(self, repo_factory: RepositoryFactory) -> None:
        """Load geographical data from database."""
        try:
            geo_repo = repo_factory.get_repository(Geo)
            geo_record = await geo_repo.get_last()
            if geo_record:
                self.geo_place = geo_record.place
                self.geo_msg = geo_record.message
                self.geo_url = geo_record.urls
            else:
                logger.error("No geo data found")
                self.has_errors = True
        except Exception as e:
            logger.error(f"Error loading geo data: {e}")
            self.has_errors = True

    async def _load_journal_data(self, repo_factory: RepositoryFactory) -> None:
        """Load journal data from database."""
        try:
            journal_repo = repo_factory.get_repository(Journal)
            journal_record = await journal_repo.get_last()
            if journal_record:
                self.journal_msg = journal_record.journal
            else:
                logger.error("No journal data found")
                self.has_errors = True
        except Exception as e:
            logger.error(f"Error loading journal data: {e}")
            self.has_errors = True

    async def load_state(self) -> None:
        """Load all state data from database."""
        logger.info("Loading state from database")
        
        now = datetime.now()
        self.datetime = now.strftime("%A, %d %B %Y | %H:%M").lower()
        self.timestamp = int(now.timestamp())
        if now.hour < JOURNAL_MESSAGE_HOUR:
            now -= timedelta(days=1)
        self.date = now.strftime("%d %b %Y").lower()
        #try:
        async with database.AsyncSessionLocal() as session:
            print(session)
            repo_factory = RepositoryFactory(session)
            # Load all data types
            await self._load_commits(repo_factory)
            await self._load_bing_data(repo_factory)
            await self._load_weather(repo_factory)
            await self._load_time_data(repo_factory)
            await self._load_geo_data(repo_factory)
            await self._load_journal_data(repo_factory)
            
            if self.has_errors:
                logger.warning("Some data failed to load")
            else:
                logger.info("All data loaded successfully")
                    
        # except Exception as e:
        #     logger.error(f"Failed to load state: {e}")
        #     self.has_errors = True

    def render_readme(self) -> bool:
        """Render README from template. Returns True if successful."""
        logger.info("Rendering README")
        
        try:
            template_path = TEMPLATES_DIR / 'README_TEMPLATE.md'
            readme_path = UI_DIR / 'README.md'
            
            if not template_path.exists():
                logger.error(f"Template not found: {template_path}")
                return False
                
            template = template_path.read_text(encoding='utf-8')
            
            readme_content = template.format(
                weather_msg=self.weather_msg,
                bing_title=self.bing_data.get("title", "-"),
                bing_url=self.bing_data.get("url", "-"),
                bing_desc=self.bing_data.get("description", "-"),
                bing_copyright=self.bing_data.get("copyright", "-"),
                timestamp=self.timestamp,
                datetime=self.datetime,
                geo_place=self.geo_place,
                geo_msg=self.geo_msg,
                geo_url=f"![Wonder]({self.geo_url})" if self.geo_url else "",
                date=self.date,
                journal_msg=self.journal_msg
            )
            
            readme_path.write_text(readme_content, encoding='utf-8')
            logger.info("README rendered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to render README: {e}")
            return False

    def write_resource_files(self) -> bool:
        """Write resource files. Returns True if successful."""
        logger.info("Writing resource files")
        
        files_to_write = [
            ('commit.txt', self.commit_msg),
            ('time-dark.svg', self.time_msg_dark),
            ('time-light.svg', self.time_msg_light)
        ]
        
        success = True
        for filename, content in files_to_write:
            try:
                file_path = UI_DIR / filename
                file_path.write_text(content, encoding='utf-8')
            except Exception as e:
                logger.error(f"Failed to write {filename}: {e}")
                success = False
                
        return success

    async def update_ui(self) -> bool:
        """Update the entire UI. Returns True if completely successful."""
        logger.info("Updating UI")
        
        await self.load_state()
        readme_success = self.render_readme()
        files_success = self.write_resource_files()
        
        overall_success = not self.has_errors and readme_success and files_success
        
        if overall_success:
            logger.info("UI update completed successfully")
        else:
            logger.warning("UI update completed with some errors")
            
        return overall_success

# Create singleton instance
state = UIState()