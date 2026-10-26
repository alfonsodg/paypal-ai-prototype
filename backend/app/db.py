import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings

if settings.database_url.startswith("sqlite:///") and not settings.database_url.startswith("sqlite:///:memory:"):
    db_path = settings.database_url.replace("sqlite:///", "", 1)
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()