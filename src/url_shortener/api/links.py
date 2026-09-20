"""Links api module that contains endpoints for creating code and get redirection by code."""
from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from url_shortener.api.dependencies import LinkServiceDep
from url_shortener.config import settings
from url_shortener.schemas.urls import (
    SAddCustomShortUrl,
    SAddLongUrl,
    SShortUrlResponse,
)

router = APIRouter()

@router.post('/shorten', response_model=SShortUrlResponse, status_code=201)
def make_short_url(data: SAddLongUrl, link_service: LinkServiceDep):
    """Creates short url via automatically generated code."""
    
    code = link_service.create_short_code(str(data.long_url)) 
    short_url = f"{settings.public_base_url.rstrip('/')}/{code}"
    return SShortUrlResponse(short_url=short_url)

@router.post('/shorten/custom', response_model=SShortUrlResponse, status_code=201)
def make_short_url_by_wanted_code(data: SAddCustomShortUrl, link_service: LinkServiceDep):
    """Creates short url via specified custom code."""
    custom_code = link_service.create_custom_shorturl(str(data.long_url), str(data.custom_code))
    short_url = f"{settings.public_base_url.rstrip('/')}/{custom_code}"
    return SShortUrlResponse(short_url=short_url)

@router.get('/{code}')
def get_short_url(code: str, link_service: LinkServiceDep):
    """Redirects to long url via specified code."""
    long_url = link_service.get_long_url(code)
    return RedirectResponse(url=long_url, status_code=302)
