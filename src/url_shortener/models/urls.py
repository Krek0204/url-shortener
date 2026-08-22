from datetime import datetime

from sqlalchemy import DateTime, text
from sqlalchemy.orm import mapped_column, Mapped

from url_shortener.db.base import Base


class UrlORM(Base):
    __tablename__ = 'urls'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str | None] = mapped_column(unique=True, nullable=True)
    long_url: Mapped[str] = mapped_column(unique=True, nullable=False)
    clicks_count: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text('now()'),
        nullable=False,
    )