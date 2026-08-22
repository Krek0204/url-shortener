from sqlalchemy import select, update
from sqlalchemy.orm import Session

from url_shortener.models.urls import UrlORM

class UrlRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_code(self, code: str) -> UrlORM | None:
        query = select(UrlORM).where(UrlORM.code == code)
        return self.session.scalar(query)
    
    def increment_clicks_by_code(self, code: str) -> None:
        query = (
            update(UrlORM)
            .where(UrlORM.code == code)
            .values(clicks_count=UrlORM.clicks_count + 1)
        )
        self.session.execute(query)
    
    def get_by_long_url(self, long_url: str) -> UrlORM | None:
        query = select(UrlORM).where(UrlORM.long_url == long_url)
        return self.session.scalar(query)
    
    def add_url(self, long_url: str, code: str | None = None) -> UrlORM:
        url = UrlORM(code=code, long_url=long_url)
        self.session.add(url)
        self.session.flush()
        return url
    