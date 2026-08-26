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
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSession()
    # Seed Synthetic Cohorts
    SyntheticDataGenerator.populate_database(
        db=db,
        customer_count=20,
        transaction_count=50,
        failure_rate=0.30,
    )
    RecoveryPlaybookService.reset_playbook()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)
    RecoveryPlaybookService.reset_playbook()


def test_simulation_baseline_run(test_db):
    sim_service = SimulationService(test_db)
    metrics = sim_service.run_baseline_simulation(limit=10)
    assert metrics.strategy_name == "BASELINE_RETRY_ONCE"
    assert metrics.cases_count > 0
    assert metrics.total_revenue_at_risk > 0


def test_simulation_ai_orchestrator_run(test_db):
    sim_service = SimulationService(test_db)
    metrics = sim_service.run_ai_simulation(limit=10, use_mock=True)
    assert metrics.strategy_name == "AI_ORCHESTRATOR"
    assert metrics.cases_count > 0
    assert metrics.total_revenue_at_risk > 0
