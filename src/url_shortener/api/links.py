from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from url_shortener.config import settings
from url_shortener.schemas.urls import SAddLongUrl, SShortUrlResponse
from url_shortener.api.dependencies import LinkServiceDep
from url_shortener.exceptions import LinkNotFoundError

router = APIRouter()

@router.post('/shorten', response_model=SShortUrlResponse, status_code=201)
def make_short_url(data: SAddLongUrl, link_service: LinkServiceDep):
    code = link_service.create_short_code(str(data.long_url))
    short_url = f"{settings.public_base_url.rstrip('/')}/{code}"
    return SShortUrlResponse(short_url=short_url)
        
    
@router.get('/{code}')
def get_short_url(code: str, link_service: LinkServiceDep):
    try:
        long_url = link_service.get_long_url(code)
        return RedirectResponse(url=long_url, status_code=301)
        
    except LinkNotFoundError as exc:
        raise HTTPException(status_code=404, detail='Long url not found') from exc
