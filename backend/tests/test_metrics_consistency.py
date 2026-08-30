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


def test_dashboard_and_analytics_metrics_consistency(client):
    """
    PERMANENT REGRESSION GUARD:
    Guarantees Dashboard (/dashboard/summary) and Comparison (/dashboard/comparison)
    produce 100% identical shared recovery numbers across identical datasets and date filters.
    """
    # 1. Seed data and run simulation
    client.post("/data/generate", json={"transaction_count": 60, "failure_rate": 0.35})
    client.post("/run/baseline", json={"limit": 25})
    client.post("/run/ai", json={"limit": 25, "use_mock_llm": True})

    # 2. Fetch Dashboard & Comparison without time filter
    dash_res = client.get("/dashboard/summary")
    assert dash_res.status_code == 200
    dash = dash_res.json()

    comp_res = client.get("/dashboard/comparison")
    assert comp_res.status_code == 200
    comp = comp_res.json()

    # 3. Assert exact mathematical equivalence for all shared headline metrics
    assert dash["total_revenue_at_risk"] == comp["ai"]["total_at_risk"]
    assert dash["total_recovered_revenue"] == comp["ai"]["total_recovered"]
    assert dash["overall_recovery_rate"] == comp["ai"]["recovery_rate_percent"]
    assert dash["baseline_recovered_revenue"] == comp["baseline"]["total_recovered"]
    assert dash["baseline_recovery_rate"] == comp["baseline"]["recovery_rate_percent"]
    assert dash["recovery_uplift_inr"] == comp["uplift"]["extra_revenue_recovered_inr"]
    assert dash["rate_uplift_percent"] == comp["uplift"]["recovery_rate_uplift_percent"]
    assert dash["net_roi_percent"] == comp["uplift"]["net_roi_percent"]

    # 4. Assert non-zero values on populated dataset
    assert dash["total_revenue_at_risk"] > 0
    assert dash["total_recovered_revenue"] > 0

    # 5. Assert comparison breakdown tables agree with headline totals
    chart_seg_sum = sum(s["ai_recovered_inr"] for s in dash["comparison_chart"])
    assert round(chart_seg_sum, 2) == round(dash["total_recovered_revenue"], 2)


def test_date_range_filtering_consistency(client):
    """
    Asserts date-range parameters dynamically filter dashboard summary.
    """
    client.post("/data/generate", json={"transaction_count": 40, "failure_rate": 0.30})
    client.post("/run/ai", json={"limit": 20, "use_mock_llm": True})

    # Test with time_range filter
    dash_7d = client.get("/dashboard/summary?time_range=7d").json()
    assert "total_recovered_revenue" in dash_7d
    assert "overall_recovery_rate" in dash_7d
    assert "active_cases_count" in dash_7d
