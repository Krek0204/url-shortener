from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker

from url_shortener.config import settings
from url_shortener.db.base import Base

database_url = URL.create(
    "postgresql+psycopg",
    username=settings.postgres_user,
    password=settings.postgres_password,
    host=settings.postgres_host,
    database=settings.postgres_db,
    port=settings.port,
)
engine = create_engine(database_url, pool_pre_ping=True)

session_fabric = sessionmaker(engine, expire_on_commit=False)

def get_session():
    with session_fabric() as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
