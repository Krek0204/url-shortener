from sqlalchemy.exc import IntegrityError

from url_shortener.services.shortener import ShortenerService
from url_shortener.repositories.urls import UrlRepository
from url_shortener.exceptions import LinkNotFoundError

class LinkService:
    
    def __init__(self, repository: UrlRepository, shortener: ShortenerService):
        self.repository = repository
        self.shortener = shortener
        
    def get_long_url(self, code: str) -> str | None:
        urlORM = self.repository.get_by_code(code)
        if urlORM is None:
            raise LinkNotFoundError(code)
        else:
            self.repository.increment_clicks_by_code(code)
            return urlORM.long_url
    
    def create_short_code(self, long_url: str) -> str | None:
        # Check if long_url already in base
        founded_url = self.repository.get_by_long_url(long_url)
        if founded_url is not None:
            if founded_url.code is None:
                founded_url.code = self.shortener.create_code(founded_url.id)
            return founded_url.code
        
        # Create short url
        try:
            urlORM = self.repository.add_url(long_url=long_url)
            urlORM.code = self.shortener.create_code(urlORM.id)
            self.repository.session.flush()
            return urlORM.code
        except IntegrityError:
            self.repository.session.rollback()
            existing = self.repository.get_by_long_url(long_url)
            if existing is None or existing.code is None:
                raise
            return existing.code
    
    