"""Module that specifies urls pydantic schemas."""
from pydantic import BaseModel, HttpUrl, Field

class SAddLongUrl(BaseModel):
    """Pydantic schema for adding long url."""
    long_url: HttpUrl = Field(max_length=2048)

class SAddCustomShortUrl(SAddLongUrl):
    """Pydantic schema for adding custom long url."""
    custom_code: str = Field(min_length=3, max_length=32, pattern=r'^[a-zA-Z0-9_-]+$')

class SShortUrlResponse(BaseModel):
    """Pydantic schema for response, that contains short url"""
    short_url: HttpUrl = Field(max_length=2048)

