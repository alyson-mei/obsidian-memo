from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional, Dict
import logging
import colorlog
from enum import Enum

# --- Enums ---
class WeatherAPI(str, Enum):
    FREEWEATHER = "freeweather"
    TOMORROWIO = "tomorrow.io"

class ModelProvider(str, Enum):
    GOOGLE_GENAI = "google_genai"

# --- Base Directory Configuration ---
BASE_DIR = Path(__file__).parent.parent

# --- Main Settings ---
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # --- API Keys ---
    freeweather_api_key: Optional[str] = Field(None, alias="FREEWEATHER_API_KEY")
    tomorrowio_api_key: Optional[str] = Field(None, alias="TOMORROWIO_API_KEY")
    openai_api_key: Optional[str] = Field(None, alias="OPENAI_API_KEY")
    google_api_key: Optional[str] = Field(None, alias="GOOGLE_API_KEY")
    tavily_api_key: Optional[str] = Field(None, alias="TAVILY_API_KEY")
    github_username: Optional[str] = Field(None, alias="GITHUB_USERNAME")
    github_api_key: Optional[str] = Field(None, alias="GITHUB_API_KEY")
    
    # --- Google Gemini ---
    model_name: str = Field("gemini-2.5-flash", alias="MODEL_NAME")
    model_name_pro: str = Field("gemini-2.5-pro", alias="MODEL_NAME_PRO")
    model_provider: ModelProvider = Field(ModelProvider.GOOGLE_GENAI, alias="MODEL_PROVIDER")
    
    # --- Default Response ---
    default_response: str = Field("Unable to generate response at this time.", alias="DEFAULT_RESPONSE")
    
    # --- Database ---
    database_url: str = Field("sqlite+aiosqlite:///app/data/app.db", alias="DATABASE_URL")
    
    # --- Repository ---
    repo_dir: Path = Field(
        default_factory=lambda: Path("/home/alyson/Applications/Obsidian/Vaults"),
        alias="REPO_DIR"
    )
    
    # --- Weather ---
    location: str = Field("Moscow", alias="LOCATION")
    tomorrowio_location: str = Field("Zyuzino,Moscow,Russia", alias="TOMORROWIO_LOCATION")
    weather_api: WeatherAPI = Field(WeatherAPI.TOMORROWIO, alias="WEATHER_API")
    
    # --- GitHub ---
    remote_url: str = Field("https://github.com/alyson-mei/obsidian-memo", alias="REMOTE_URL")
    
    # --- General Settings ---
    timeout: int = Field(60, alias="TIMEOUT")
    
    # --- Message Intervals ---
    num_last_commit_msg: int = Field(25, alias="NUM_LAST_COMMIT_MSG")
    num_new_commit_msg: int = Field(15, alias="NUM_NEW_COMMIT_MSG")
    num_last_search_msg: int = Field(35, alias="NUM_LAST_SEARCH_MSG")
    num_last_journal_msg: int = Field(10, alias="NUM_LAST_JOURNAL_MSG")
    
    # --- Time Intervals ---
    time_message_interval: int = Field(1, alias="TIME_MESSAGE_INTERVAL", description="minutes - every minute")
    bing_message_interval: int = Field(60, alias="BING_MESSAGE_INTERVAL", description="minutes - every hour")
    
    @field_validator('weather_commit_interval')
    @classmethod
    def set_weather_commit_interval(cls, v, info):
        # Default to num_new_commit_msg if not explicitly set
        if info.data.get('num_new_commit_msg') is not None:
            return info.data['num_new_commit_msg']
        return v
    
    weather_commit_interval: int = Field(15, alias="WEATHER_COMMIT_INTERVAL", description="minutes - every 15 minutes (quarters)")
    
    # --- Scheduled Times ---
    geo_message_time: str = Field("10:00", alias="GEO_MESSAGE_TIME", description="daily at 10:00")
    geo_message_hour: int = Field(10, alias="GEO_MESSAGE_HOUR")
    geo_message_minute: int = Field(0, alias="GEO_MESSAGE_MINUTE")
    journal_message_time: str = Field("23:00", alias="JOURNAL_MESSAGE_TIME")
    journal_message_hour: int = Field(23, alias="JOURNAL_MESSAGE_HOUR")
    journal_message_minute: int = Field(0, alias="JOURNAL_MESSAGE_MINUTE")
    
    # --- Git Settings ---
    max_commits_before_rebase: int = Field(720, alias="MAX_COMMITS_BEFORE_REBASE")
    default_branch: str = Field("main", alias="DEFAULT_BRANCH")
    force_push_on_startup: bool = Field(True, alias="FORCE_PUSH_ON_STARTUP")
    force_push_schedule_hour: Optional[int] = Field(None, alias="FORCE_PUSH_SCHEDULE_HOUR")
    force_push_schedule_minute: Optional[int] = Field(None, alias="FORCE_PUSH_SCHEDULE_MINUTE")
    
    @field_validator('geo_message_hour', 'journal_message_hour', 'force_push_schedule_hour')
    @classmethod
    def validate_hour(cls, v):
        if v is not None and not (0 <= v <= 23):
            raise ValueError('Hour must be between 0 and 23')
        return v
    
    @field_validator('geo_message_minute', 'journal_message_minute', 'force_push_schedule_minute')
    @classmethod
    def validate_minute(cls, v):
        if v is not None and not (0 <= v <= 59):
            raise ValueError('Minute must be between 0 and 59')
        return v
    
    @field_validator('repo_dir', mode='before')
    @classmethod
    def convert_repo_dir_to_path(cls, v):
        if isinstance(v, str):
            return Path(v)
        return v
    
    @model_validator(mode='after')
    def validate_weather_api_keys(self):
        if self.weather_api == WeatherAPI.FREEWEATHER and not self.freeweather_api_key:
            raise ValueError('freeweather_api_key is required when using freeweather API')
        elif self.weather_api == WeatherAPI.TOMORROWIO and not self.tomorrowio_api_key:
            raise ValueError('tomorrowio_api_key is required when using tomorrow.io API')
        return self
    
    # --- Computed Properties ---
    @property
    def app_dir(self) -> Path:
        return BASE_DIR / "app"
    
    @property
    def assets_dir(self) -> Path:
        return self.app_dir / "assets"
    
    @property
    def ui_dir(self) -> Path:
        return self.app_dir / "presentation/ui"
    
    @property
    def data_dir(self) -> Path:
        return self.app_dir / "data"
    
    @property
    def templates_dir(self) -> Path:
        return self.assets_dir / "templates"
    
    @property
    def readme_path(self) -> Path:
        return self.ui_dir / "README.md"
    
    @property
    def commit_msg_path(self) -> Path:
        return self.ui_dir / "commit.txt"
    
    @property
    def time_dark_svg_path(self) -> Path:
        return self.ui_dir / "time-dark.svg"
    
    @property
    def time_light_svg_path(self) -> Path:
        return self.ui_dir / "time-light.svg"
    
    @property
    def freeweather_url(self) -> str:
        return f"http://api.weatherapi.com/v1/current.json?key={self.freeweather_api_key}&q={self.location}&aqi=no"
    
    @property
    def tomorrowio_url(self) -> str:
        return f"https://api.tomorrow.io/v4/weather/realtime?location={self.tomorrowio_location}&apikey={self.tomorrowio_api_key}"
    
    @property
    def weather_url(self) -> str:
        if self.weather_api == WeatherAPI.FREEWEATHER:
            return self.freeweather_url
        else:
            return self.tomorrowio_url

# --- Logging Configuration ---
class LoggerConfig(BaseModel):
    color: str
    indent: int

class LoggingSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Logger configurations
    logger_settings: Dict[str, LoggerConfig] = {
        'database': LoggerConfig(color='green', indent=6),
        'service': LoggerConfig(color='cyan', indent=6),
        'generator': LoggerConfig(color='lavender', indent=4),
        'ui': LoggerConfig(color='peach', indent=2),
        'main': LoggerConfig(color='cream', indent=0),
        'default': LoggerConfig(color='cream', indent=0)
    }

# --- Custom Logging Setup ---
def setup_colorlog_colors():
    """Setup custom colors for colorlog"""
    colorlog.escape_codes.escape_codes.update({
        # Light/pastel colors using standard ANSI
        'light_green': '\033[92m',
        'light_blue': '\033[94m', 
        'light_purple': '\033[95m',
        'light_cyan': '\033[96m',
        
        # Pastel colors using 256-color palette
        'mint': '\033[38;5;121m',
        'sky_blue': '\033[38;5;117m',
        'lavender': '\033[38;5;183m',
        'peach': '\033[38;5;216m',
        'coral': '\033[38;5;209m',
        'pink': '\033[38;5;205m',
        'sage': '\033[38;5;151m',
        'powder_blue': '\033[38;5;152m',
        'lilac': '\033[38;5;189m',
        'seafoam': '\033[38;5;158m',
        'periwinkle': '\033[38;5;147m',
        'rose': '\033[38;5;217m',
        'aqua': '\033[38;5;159m',
        'blush': '\033[38;5;224m',
        'teal': '\033[38;5;123m',
        'soft_yellow': '\033[38;5;229m',
        'pale_green': '\033[38;5;194m',
        'ice_blue': '\033[38;5;195m',
        'cream': '\033[38;5;230m',
        'dusty_rose': '\033[38;5;181m',
    })

class CustomFormatter(colorlog.ColoredFormatter):
    def __init__(self, logging_settings: LoggingSettings):
        super().__init__()
        self.logging_settings = logging_settings
        
    def format(self, record):
        settings = self.logging_settings.logger_settings['default']
        for postfix, config in self.logging_settings.logger_settings.items():
            if postfix != 'default' and record.name.endswith(postfix):
                settings = config
                break
        self.log_colors = {record.levelname: settings.color}
        return super().format(record)

def setup_logger(name: str, indent: int = 0, logging_settings: Optional[LoggingSettings] = None) -> logging.Logger:
    if logging_settings is None:
        logging_settings = LoggingSettings()
    
    setup_colorlog_colors()
    
    handler = colorlog.StreamHandler()
    
    formatter = CustomFormatter(logging_settings)
    formatter._style._fmt = (" " * indent) + "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter.reset = True
    formatter.log_colors = {}  # Empty, will be set in format()
    
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False
    return logger

# --- Create global settings instance ---
settings = Settings()
logging_settings = LoggingSettings()

UI_DIR, TEMPLATES_DIR, NUM_NEW_COMMIT_MSG, JOURNAL_MESSAGE_HOUR, REPO_DIR, README_PATH, COMMIT_MSG_PATH, TIME_DARK_SVG_PATH, TIME_LIGHT_SVG_PATH, FREEWEATHER_URL, TOMORROWIO_URL, WEATHER_URL = (
    settings.ui_dir,
    settings.templates_dir,
    settings.num_new_commit_msg,
    settings.journal_message_hour,
    settings.repo_dir,
    settings.readme_path,
    settings.commit_msg_path,
    settings.time_dark_svg_path,
    settings.time_light_svg_path,
    settings.freeweather_url,
    settings.tomorrowio_url,
    settings.weather_url
)

GITHUB_USERNAME = settings.github_username
GITHUB_API_KEY = settings.github_api_key
REMOTE_URL = settings.remote_url
TIME_MESSAGE_INTERVAL = settings.time_message_interval
BING_MESSAGE_INTERVAL = settings.bing_message_interval
WEATHER_COMMIT_INTERVAL = settings.weather_commit_interval
GEO_MESSAGE_TIME = settings.geo_message_time
GEO_MESSAGE_HOUR = settings.geo_message_hour
GEO_MESSAGE_MINUTE = settings.geo_message_minute
JOURNAL_MESSAGE_TIME = settings.journal_message_time
JOURNAL_MESSAGE_HOUR = settings.journal_message_hour
JOURNAL_MESSAGE_MINUTE = settings.journal_message_minute
MAX_COMMITS_BEFORE_REBASE = settings.max_commits_before_rebase
DEFAULT_BRANCH = settings.default_branch
FORCE_PUSH_ON_STARTUP = settings.force_push_on_startup
FORCE_PUSH_SCHEDULE_HOUR = settings.force_push_schedule_hour
FORCE_PUSH_SCHEDULE_MINUTE = settings.force_push_schedule_minute    


# --- Export for convenience ---
__all__ = ['settings', 'logging_settings', 'setup_logger']