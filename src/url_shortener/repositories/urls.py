from sqlalchemy import select, update
from sqlalchemy.orm import Session

from url_shortener.models.urls import UrlORM, AliasORM

class UrlRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_code(self, code: str) -> UrlORM | None:
        query = select(UrlORM).where(UrlORM.aliases.any(AliasORM.code == code))
        return self.session.scalar(query)
   
    def increment_clicks_by_code(self, code: str) -> None:
        query = (
            update(UrlORM)
            .where(UrlORM.aliases.any(AliasORM.code == code))
            .values(clicks_count=UrlORM.clicks_count + 1)
        )
        self.session.execute(query)

    def get_by_long_url(self, long_url: str) -> UrlORM | None:
        query = select(UrlORM).where(UrlORM.long_url == long_url)
        return self.session.scalar(query)

    def add_url(self, long_url: str) -> UrlORM:
        url = UrlORM(long_url=long_url)
        self.session.add(url)
        self.session.flush()
        return url

    def add_alias(self, url: UrlORM, code: str, is_custom: bool = False) -> AliasORM:
        alias = AliasORM(code=code, is_custom=is_custom)
        url.aliases.append(alias)
        self.session.flush()
        return alias
