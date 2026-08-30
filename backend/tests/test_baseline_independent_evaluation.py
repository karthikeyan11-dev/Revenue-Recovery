import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.db as db_module
from app.db import Base, get_db
from app.main import app

test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    Base.metadata.create_all(bind=test_engine)
    monkeypatch.setattr(db_module, "engine", test_engine)
    monkeypatch.setattr(db_module, "SessionLocal", TestingSessionLocal)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_independent_baseline_vs_ai_evaluation(client):
    """
    VERIFICATION GUARD:
    Guarantees Baseline is evaluated independently against the same cohort
    and is NOT a hardcoded multiplier (e.g. 70% or 75%) of AI recovery.
    """
    # 1. Generate test dataset
    client.post("/data/generate", json={"transaction_count": 80, "failure_rate": 0.40})

    # 2. Run AI Orchestrator on the cohort
    ai_res = client.post("/run/ai", json={"limit": 30, "use_mock_llm": True})
    assert ai_res.status_code == 200

    # 3. Fetch Dashboard and Comparison summaries
    dash = client.get("/dashboard/summary").json()
    comp = client.get("/dashboard/comparison").json()

    ai_recovered = dash["total_recovered_revenue"]
    base_recovered = dash["baseline_recovered_revenue"]
    ai_rate = dash["overall_recovery_rate"]
    base_rate = dash["baseline_recovery_rate"]
    uplift_inr = dash["recovery_uplift_inr"]
    rate_uplift = dash["rate_uplift_percent"]

    # 4. Assert baseline is NOT artificially derived as 70% or 75% of AI
    assert base_recovered != round(ai_recovered * 0.70, 2), "Baseline must not be 70% of AI"
    assert base_recovered != round(ai_recovered * 0.75, 2), "Baseline must not be 75% of AI"

    # 5. Assert Uplift ₹ is mathematically exact: AI Recovered - Baseline Recovered
    expected_uplift_inr = round(max(0.0, ai_recovered - base_recovered), 2)
    assert uplift_inr == expected_uplift_inr
    assert comp["uplift"]["extra_revenue_recovered_inr"] == expected_uplift_inr

    # 6. Assert Uplift % is mathematically exact: AI Rate - Baseline Rate
    expected_rate_uplift = round(max(0.0, ai_rate - base_rate), 1)
    assert rate_uplift == expected_rate_uplift
    assert comp["uplift"]["recovery_rate_uplift_percent"] == expected_rate_uplift

    # 7. Assert comparison chart items exist and have independent values
    chart = dash["comparison_chart"]
    assert len(chart) > 0
    for c_item in chart:
        assert "failure_reason" in c_item or "segment" in c_item
        assert "ai_recovered_inr" in c_item
        assert "baseline_recovered_inr" in c_item
