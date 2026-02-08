"""Configuration for OpenProject MCP Server."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """OpenProject MCP Server settings."""

    # OpenProject API settings
    url: str = "http://77.232.130.90:8085"
    api_key: str = ""

    # Query IDs for board columns
    query_id_bugs: int = 1390  # Колонка "Баги"
    query_id_ready: int = 1378  # Колонка "Готово к разработке"

    # Custom field for AI dev flag
    ai_dev_field: str = "customField2"

    model_config = {
        "env_prefix": "OPENPROJECT_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()

