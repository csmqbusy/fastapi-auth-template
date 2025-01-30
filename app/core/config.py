from pathlib import Path

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_correct_cwd(sources_dir_name: str = "app") -> Path:
    """
    This function is needed to correctly launch the application from
    the app/main.py file and alembic commands from the project root folder.
    """
    cwd = Path.cwd()
    if cwd.name == sources_dir_name:
        cwd = cwd.parent
    return cwd


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class ApiPrefix(BaseModel):
    prefix: str = "/api"


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
            env_file=get_correct_cwd() / ".env.dev",
            case_sensitive=False,
            env_nested_delimiter="__",
    )

    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    db: DatabaseConfig


settings = Settings()
