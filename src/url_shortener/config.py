"""
This module used to specify settings for application. 
Settings specified with .env file or Environments vars.
"""


from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Class for specifing settings. Used pydantic_settings."""
    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',
        )

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    port: int
    public_base_url: str
    cors_origins: list[str]

settings = Settings()
