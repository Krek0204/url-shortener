from pydantic import BaseModel, HttpUrl, Field

class SAddLongUrl(BaseModel):
    long_url: HttpUrl = Field(max_length=2048)
    
class SAddCustomShortUrl(SAddLongUrl):
    custom_code: str = Field(min_length=3, max_length=32, pattern=r'^[a-zA-Z0-9_-]+$')
    
class SShortUrlResponse(BaseModel):
    short_url: HttpUrl = Field(max_length=2048)

