from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        extra='allow',
        )
    
    database_url: str
    public_base_url: str
    
settings = Settings()