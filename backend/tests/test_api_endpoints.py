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


def test_root_endpoint(client):
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "AI Revenue Recovery Orchestrator"
    assert data["health_url"] == "/health"


def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"


def test_data_generation_and_simulation_flow(client):
    # 1. Generate synthetic dataset
    gen_res = client.post("/data/generate", json={"transaction_count": 50, "failure_rate": 0.30})
    assert gen_res.status_code == 201
    gen_data = gen_res.json()
    assert gen_data["transactions_generated"] == 50
    assert gen_data["failures_generated"] > 0

    # 2. Run Baseline simulation
    base_res = client.post("/run/baseline", json={"limit": 20})
    assert base_res.status_code == 200
    base_data = base_res.json()
    assert base_data["strategy"] == "BASELINE_RETRY_ONCE"
    assert "metrics" in base_data

    # 3. Run AI Orchestrator simulation
    ai_res = client.post("/run/ai", json={"limit": 20, "use_mock_llm": True})
    assert ai_res.status_code == 200
    ai_data = ai_res.json()
    assert ai_data["strategy"] == "AI_ORCHESTRATOR"
    assert ai_data["cases_processed"] > 0

    # 4. Fetch Cases List
    cases_res = client.get("/cases")
    assert cases_res.status_code == 200
    cases_data = cases_res.json()
    assert len(cases_data["items"]) > 0

    # 5. Fetch First Case Detail with Timeline
    first_case_id = cases_data["items"][0]["id"]
    detail_res = client.get(f"/cases/{first_case_id}")
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["id"] == first_case_id
    assert len(detail_data["timeline"]) > 0

    # 6. Fetch Dashboard Summary
    dash_res = client.get("/dashboard/summary")
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["total_revenue_at_risk"] > 0

    # 7. Fetch Agent Activity Feed
    agent_res = client.get("/agents/activity?limit=10")
    assert agent_res.status_code == 200
    agent_data = agent_res.json()
    assert len(agent_data["activities"]) > 0
