"""
This module contains link service, that used to handle main application logic.
It creates short code, custom short code, gets long url.
"""
from sqlalchemy.exc import IntegrityError

from url_shortener.exceptions import (
    CodeAlreadyTakenError,
    CodeNotFoundError,
    CustomCodeAlreadyTakenError,
    LinkNotFoundError,
)
from url_shortener.models.urls import AliasORM
from url_shortener.repositories.urls import UrlRepository
from url_shortener.services.shortener import ShortenerService


class LinkService:
    """Link Service class, that handles main application logic."""

    def __init__(self, repository: UrlRepository, shortener: ShortenerService):
        self.repository = repository
        self.shortener = shortener
 
    def get_long_url(self, code: str) -> str:
        """Getting long url by short code."""
        urlORM = self.repository.get_by_code(code)
        if urlORM is None:
            raise LinkNotFoundError(code)
        else:
            self.repository.increment_clicks_by_code(code)
            return urlORM.long_url

    def create_short_code(self, long_url: str) -> str:
        """Creating short code for long_url automatically."""
        # Check if long_url already in base
        founded_url = self.repository.get_by_long_url(long_url)
        if founded_url is not None:
            if not self.has_url_auto_code(founded_url.aliases):
                code = self.shortener.create_code(founded_url.id)
                try:
                    alias = self.repository.add_alias(founded_url, code)
                except IntegrityError:
                    self.repository.session.rollback()
                    refreshed = self.repository.get_by_long_url(long_url)
                    if refreshed is not None:
                        return self.get_url_auto_code(refreshed.aliases)
                    else:
                        # Unknown inner error
                        raise
                return alias.code
            else:
                return self.get_url_auto_code(founded_url.aliases)

        # Create short url
        try:
            url_orm = self.repository.add_url(long_url=long_url)
            code = self.shortener.create_code(url_orm.id)
            try:
                alias = self.repository.add_alias(url=url_orm, code=code)
            except IntegrityError as exc:
                raise CodeAlreadyTakenError(code) from exc
            return alias.code
        except IntegrityError:
            self.repository.session.rollback()
            existing = self.repository.get_by_long_url(long_url)
            if existing is None or not existing.aliases:
                raise
            return self.get_url_auto_code(existing.aliases)

    def create_custom_shorturl(self, long_url: str, custom_code: str) -> str:
        """Creating custom short code for long url (alias)."""
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
                url_orm = self.repository.add_url(long_url=long_url)
                try:
                    alias = self.repository.add_alias(url=url_orm, code=custom_code, is_custom=True)
                except IntegrityError as exc:
                    raise CustomCodeAlreadyTakenError(custom_code) from exc
                return alias.code
            except IntegrityError:
                self.repository.session.rollback()
                existing = self.repository.get_by_long_url(long_url)
                if existing is None or not existing.aliases:
                    raise
                return self.get_url_custom_code(existing.aliases, custom_code=custom_code)

    def has_url_auto_code(self, aliases: list[AliasORM]) -> bool:
        """Checking, if one of url aliases is automatically generated code"""
        for alias in aliases:
            if alias.is_custom is False:
                return True
        return False

    def get_url_auto_code(self, aliases: list[AliasORM]) -> str:
        """Get automatically generated code from aliases list"""
        for alias in aliases:
            if alias.is_custom is False:
                return alias.code
        raise CodeNotFoundError("autocode")

    def get_url_custom_code(self, aliases: list[AliasORM], custom_code: str) -> str:
        """Get custom code from aliases by specifing it name."""
        for alias in aliases:
            if alias.code == custom_code:
                return custom_code
        raise CodeNotFoundError(custom_code)
