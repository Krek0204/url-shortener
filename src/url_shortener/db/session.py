from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from url_shortener.config import settings
from url_shortener.db.base import Base

engine = create_engine(settings.database_url)

session_fabric = sessionmaker(engine, expire_on_commit=False)

def get_session():
    with session_fabric() as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        
def setup_db() -> None:
    with engine.begin() as conn:
        Base.metadata.create_all(conn)