import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Database path relative to the backend directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "parental_task_app.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Use the non-deprecated declarative_base import
Base = declarative_base()


def get_db():
    """
    Yields a database session and ensures it's closed after use.
    Used as a context manager or dependency.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
