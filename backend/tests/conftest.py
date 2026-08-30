import os
import tempfile

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.integrations.vectorstore.chroma_provider import RecoveryPlaybookService


@pytest.fixture(autouse=True, scope="session")
def isolate_test_chromadb():
    """
    Isolates ChromaDB to an isolated temporary directory during pytest runs,
    preventing test fixtures from wiping the live shared data/chroma_db/recovery_playbook collection.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        old_dir = os.environ.get("CHROMA_PERSIST_DIR")
        os.environ["CHROMA_PERSIST_DIR"] = temp_dir
        # Reset cached client so it binds to the isolated temporary directory
        RecoveryPlaybookService._client = None
        RecoveryPlaybookService._collection = None
        yield temp_dir
        if old_dir is not None:
            os.environ["CHROMA_PERSIST_DIR"] = old_dir
        else:
            os.environ.pop("CHROMA_PERSIST_DIR", None)
        RecoveryPlaybookService._client = None
        RecoveryPlaybookService._collection = None


@pytest.fixture
def memory_db():
    """Provides an in-memory SQLite database session for unit tests."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)
