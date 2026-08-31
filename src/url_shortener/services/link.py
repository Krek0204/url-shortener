from sqlalchemy.exc import IntegrityError

from url_shortener.services.shortener import ShortenerService
from url_shortener.repositories.urls import UrlRepository
from url_shortener.exceptions import LinkNotFoundError, CodeAlreadyTakenError, CustomCodeAlreadyTakenError, CodeNotFoundError
from url_shortener.models.urls import AliasORM

class LinkService:
    
    def __init__(self, repository: UrlRepository, shortener: ShortenerService):
        self.repository = repository
        self.shortener = shortener
        
    def get_long_url(self, code: str) -> str:
        urlORM = self.repository.get_by_code(code)
        if urlORM is None:
            raise LinkNotFoundError(code)
        else:
            self.repository.increment_clicks_by_code(code)
            return urlORM.long_url
    
    def create_short_code(self, long_url: str) -> str:
        # Check if long_url already in base
        founded_url = self.repository.get_by_long_url(long_url)
        if founded_url is not None:
            if not self.hasUrlAutoCode(founded_url.aliases):
                code = self.shortener.create_code(founded_url.id)
                try:
                    alias = self.repository.add_alias(founded_url, code)
                except IntegrityError:
                    self.repository.session.rollback()
                    refreshed = self.repository.get_by_long_url(long_url)
                    return self.getUrlAutoCode(refreshed.aliases)
                return alias.code
            else:
                return self.getUrlAutoCode(founded_url.aliases)
        
        # Create short url
        try:
            urlORM = self.repository.add_url(long_url=long_url)
            code = self.shortener.create_code(urlORM.id)
            try:
                alias = self.repository.add_alias(url=urlORM, code=code)
            except IntegrityError as exc:
                raise CodeAlreadyTakenError(code) from exc
            return alias.code
        except IntegrityError:
            self.repository.session.rollback()
            existing = self.repository.get_by_long_url(long_url)
            if existing is None or not existing.aliases:
                raise
            return self.getUrlAutoCode(existing.aliases)
        
    def create_custom_shorturl(self, long_url: str, custom_code: str) -> str:
        founded_custom_url = self.repository.get_by_code(custom_code)
        if founded_custom_url is not None:
            if founded_custom_url.long_url == long_url:
                return custom_code
            else:
                raise CustomCodeAlreadyTakenError(custom_code)
        
        founded_long_url = self.repository.get_by_long_url(long_url)
        if founded_long_url is not None:
            try:
                alias = self.repository.add_alias(founded_long_url, custom_code, is_custom=True)
            except IntegrityError as exc:
                raise CustomCodeAlreadyTakenError(custom_code) from exc
            return alias.code
        else:
            try:
                urlORM = self.repository.add_url(long_url=long_url)
                try:
                    alias = self.repository.add_alias(url=urlORM, code=custom_code, is_custom=True)
                except IntegrityError as exc:
                    raise CustomCodeAlreadyTakenError(custom_code) from exc
                return alias.code
            except IntegrityError:
                self.repository.session.rollback()
                existing = self.repository.get_by_long_url(long_url)
                if existing is None or not existing.aliases:
                    raise
                return self.getUrlCustomCode(existing.aliases, custom_code=custom_code)
        
    def hasUrlAutoCode(self, aliases: list[AliasORM]) -> bool:
        for alias in aliases:
            if alias.is_custom is False:
                return True
        return False
    
    def getUrlAutoCode(self, aliases: list[AliasORM]) -> str:
        for alias in aliases:
            if alias.is_custom is False:
                return alias.code
        raise CodeNotFoundError("autocode")
    
    def getUrlCustomCode(self, aliases: list[AliasORM], custom_code: str) -> str:
        for alias in aliases:
            if alias.code == custom_code:
                return custom_code
        raise CodeNotFoundError(custom_code)

    