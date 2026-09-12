from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from url_shortener.db.session import get_session
from url_shortener.services.shortener import ShortenerService
from url_shortener.services.link import LinkService
from url_shortener.repositories.urls import UrlRepository

SessionDep = Annotated[Session, Depends(get_session)]

def get_url_repository(_session: SessionDep) -> UrlRepository:
    return UrlRepository(session=_session)

RepoDep = Annotated [UrlRepository, Depends(get_url_repository)]


def get_shortener_service() -> ShortenerService:
    return ShortenerService()

ShortenerDep = Annotated[ShortenerService, Depends(get_shortener_service)]


def get_link_service(repo: RepoDep, shortener_service: ShortenerDep) -> LinkService:
    return LinkService(repository=repo, shortener=shortener_service)

LinkServiceDep = Annotated[LinkService, Depends(get_link_service)]
