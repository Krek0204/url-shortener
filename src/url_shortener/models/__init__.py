"""Init module for specifing models, that needs export."""
from url_shortener.models.urls import UrlORM, AliasORM

__all__ = ["UrlORM", "AliasORM"]
