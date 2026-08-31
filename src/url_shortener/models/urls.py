from datetime import datetime
from typing import List

from sqlalchemy import DateTime, text, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from url_shortener.db.base import Base


class UrlORM(Base):
    __tablename__ = 'urls'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    long_url: Mapped[str] = mapped_column(unique=True, nullable=False)
    clicks_count: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text('now()'),
        nullable=False,
    )
    
    aliases: Mapped[List["AliasORM"]] = relationship(back_populates='url')

class AliasORM(Base):
    __tablename__ = 'aliases'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(unique=True, nullable=False)
    long_url_id: Mapped[int] = mapped_column(ForeignKey("urls.id"), nullable=False)
    is_custom: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    url: Mapped["UrlORM"] = relationship(back_populates='aliases')
     
