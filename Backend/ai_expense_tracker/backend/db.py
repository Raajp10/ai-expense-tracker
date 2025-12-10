from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# DB file is in project root: ../expense.db
SQLALCHEMY_DATABASE_URL = "sqlite:///../expense.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency: gives a DB session to each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
