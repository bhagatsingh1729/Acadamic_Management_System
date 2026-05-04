from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base  # Fix: moved from deprecated sqlalchemy.ext.declarative

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


def get_db():
    """
    Dependency that provides a database session per request and
    ensures it is properly closed afterwards.
    Moved here from routes.py so it can be reused across all route files.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


"""
Note:
- This module sets up the database connection.
- 'engine' establishes a connection with the DB.
- 'Base' is the declarative base class that all models inherit from.
- 'get_db' is a FastAPI dependency that yields a session and closes it after each request.
"""
