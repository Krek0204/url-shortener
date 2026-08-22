from pydantic import BaseModel, HttpUrl, Field

class SAddLongUrl(BaseModel):
    long_url: HttpUrl = Field(max_length=2048)
    
class SShortUrlResponse(BaseModel):
    short_url: HttpUrl = Field(max_length=2048)
    
