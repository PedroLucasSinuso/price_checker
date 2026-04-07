from enum import Enum
from pydantic_settings import BaseSettings

class DatabaseType(str, Enum):
    POSTGRES = "postgres"
    SQLITE = "sqlite"

class Settings(BaseSettings):
    postgres_url: str = ""
    sqlite_url: str = ""
    default_db: DatabaseType = DatabaseType.SQLITE
    cache_refresh_interval: int = 3600  # in seconds

    model_config = {
        "env_file": ".env"
    }

settings = Settings()