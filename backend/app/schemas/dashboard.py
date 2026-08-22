from pydantic import BaseModel, Field

from app.schemas.analyst import StrategyMetrics


class RecoveryComparisonChartItem(BaseModel):
    segment: str = Field(description="Customer cohort or leak category")
    baseline_recovered_inr: float = Field(description="INR recovered under baseline")
    ai_recovered_inr: float = Field(description="INR recovered under AI orchestrator")
    total_at_risk_inr: float = Field(description="Total at-risk revenue")


class DashboardMetricsResponse(BaseModel):
    """Headline metrics for the Executive Dashboard."""

    total_revenue_at_risk: float = Field(ge=0, description="Total INR value of payment leaks")
    total_recovered_revenue: float = Field(
        ge=0, description="Total INR recovered by AI Orchestrator"
    )
    overall_recovery_rate: float = Field(
        ge=0.0, le=100.0, description="AI recovery rate percentage"
    )
    net_roi_percent: float = Field(description="Net ROI percentage after costs")
    baseline_recovery_rate: float = Field(
        ge=0.0, le=100.0, description="Baseline recovery rate percentage"
    )
    recovery_uplift_inr: float = Field(description="Net additional INR won over baseline")
    active_cases_count: int = Field(ge=0, description="Open and In-Progress recovery cases")
    escalated_cases_count: int = Field(ge=0, description="Cases requiring human attention")
    policy_interventions_count: int = Field(
        ge=0, description="Actions blocked or modified by policy gate"
    )
    comparison_chart: list[RecoveryComparisonChartItem] = Field(
        default=[], description="Segment-by-segment comparison"
    )
    baseline_summary: StrategyMetrics | None = None
    ai_summary: StrategyMetrics | None = None
