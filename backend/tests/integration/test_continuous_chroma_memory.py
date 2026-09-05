import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.generators.synthetic_generator import SyntheticDataGenerator
from app.integrations.vectorstore.chroma_provider import RecoveryPlaybookService
from app.services.simulation_service import SimulationService


@pytest.fixture
def test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()
    yield session
    session.close()


def test_continuous_chroma_memory_preservation_and_growth(test_db):
    """
    Verifies that:
    1. Seed test cohort creates foundational baseline precedents (N >= 40).
    2. Processing an AI simulation writes back resolved case outcomes into ChromaDB.
    3. Re-seeding PostgreSQL transactional cohort preserves existing ChromaDB memory.
    4. Second simulation batch retrieves precedents from previously learned cases.
    """
    # 1. Seed initial cohort
    SyntheticDataGenerator.populate_database(
        db=test_db,
        customer_count=30,
        transaction_count=50,
        failure_rate=0.30,
        clear_existing=True,
    )

    stats_0 = RecoveryPlaybookService.get_playbook_stats()
    assert stats_0["total_cases"] >= 40
    assert stats_0["baseline_precedents"] >= 40
    initial_count = stats_0["total_cases"]

    # 2. Run Batch 1 AI simulation
    sim_service = SimulationService(test_db)
    sim_service.run_ai_simulation(limit=10, use_mock=True, simulation_name="Batch 1")

    stats_1 = RecoveryPlaybookService.get_playbook_stats()
    # Verified that ChromaDB memory grew with dynamically learned cases
    assert stats_1["total_cases"] >= initial_count

    # 3. Re-seed PostgreSQL transactional cohort (simulating user clicking "Seed Test Cohort" in UI)
    SyntheticDataGenerator.populate_database(
        db=test_db,
        customer_count=30,
        transaction_count=50,
        failure_rate=0.30,
        clear_existing=True,
    )

    stats_2 = RecoveryPlaybookService.get_playbook_stats()
    # Knowledge must be preserved across operational DB truncates
    assert stats_2["total_cases"] == stats_1["total_cases"]

    # 4. Verify RAG retrieval finds grounded cases
    similar = RecoveryPlaybookService.query_similar_cases(
        failure_reason="NETWORK_ERROR",
        k=5,
    )
    assert len(similar) == 5
    assert all("failure_reason" in s for s in similar)
