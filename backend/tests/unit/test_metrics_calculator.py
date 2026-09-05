from app.analytics.metrics import RecoveryMetricsCalculator
from app.analytics.roi import ROICalculator


def test_recovery_metrics_calculation():
    metrics = RecoveryMetricsCalculator.calculate_strategy_metrics(
        strategy_name="TEST_STRATEGY",
        total_at_risk=20000.0,
        total_recovered=15000.0,
        total_cost=500.0,
        cases_count=20,
        recovered_cases_count=15,
        escalated_count=2,
        rejected_count=1,
    )
    assert metrics.recovery_rate_percent == 75.0
    assert metrics.net_roi_percent == 72.5
    assert metrics.total_revenue_at_risk == 20000.0
    assert metrics.total_recovered_revenue == 15000.0
    assert metrics.cases_count == 20
    assert metrics.recovered_cases_count == 15


def test_roi_calculator():
    net_recovery = ROICalculator.calculate_net_recovery(15000.0, 500.0)
    assert net_recovery == 14500.0

    roi_pct = ROICalculator.calculate_roi_percentage(15000.0, 500.0)
    assert roi_pct == 2900.0

    cb_ratio = ROICalculator.calculate_cost_benefit_ratio(15000.0, 500.0)
    assert cb_ratio == 30.0


def test_metrics_comparison():
    base = RecoveryMetricsCalculator.calculate_strategy_metrics(
        strategy_name="BASELINE",
        total_at_risk=10000.0,
        total_recovered=4000.0,
        total_cost=200.0,
        cases_count=10,
        recovered_cases_count=4,
    )
    ai = RecoveryMetricsCalculator.calculate_strategy_metrics(
        strategy_name="AI_ORCHESTRATOR",
        total_at_risk=10000.0,
        total_recovered=7500.0,
        total_cost=350.0,
        cases_count=10,
        recovered_cases_count=8,
    )

    comparison = RecoveryMetricsCalculator.compare(base, ai)
    assert comparison.uplift_inr == 3500.0
    assert comparison.uplift_percent == 35.0
    assert len(comparison.key_findings) == 3
