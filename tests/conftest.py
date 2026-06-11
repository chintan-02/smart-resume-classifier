import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.db import Base
import database.models  # noqa: F401


@pytest.fixture
def temp_database_url(tmp_path) -> str:
    return f"sqlite:///{tmp_path / 'test_resumeiq.db'}"


@pytest.fixture
def test_db_session(temp_database_url):
    engine = create_engine(temp_database_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
