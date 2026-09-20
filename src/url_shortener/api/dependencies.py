"""Module uses for specifing dependency injections."""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from url_shortener.db.session import get_session
from url_shortener.repositories.urls import UrlRepository
from url_shortener.services.link import LinkService
from url_shortener.services.shortener import ShortenerService

SessionDep = Annotated[Session, Depends(get_session)]

def get_url_repository(_session: SessionDep) -> UrlRepository:
    """Getting url repository for di."""
    return UrlRepository(session=_session)

RepoDep = Annotated [UrlRepository, Depends(get_url_repository)]


def get_shortener_service() -> ShortenerService:
    """Getting shortener service for di."""
    return ShortenerService()

ShortenerDep = Annotated[ShortenerService, Depends(get_shortener_service)]


def get_link_service(repo: RepoDep, shortener_service: ShortenerDep) -> LinkService:
    """Getting link service for di."""
    return LinkService(repository=repo, shortener=shortener_service)

LinkServiceDep = Annotated[LinkService, Depends(get_link_service)]
