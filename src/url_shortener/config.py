from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        extra='allow',
        )
    
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    public_base_url: str
    
settings = Settings()