"""Session module that specifing create session function and creates engine for database."""
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker

from url_shortener.config import settings

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
    """Creates session for database."""
    
    with session_fabric() as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
