from pydantic import BaseModel, Field


class StrategyMetrics(BaseModel):
    """Aggregate performance metrics for a simulation run."""

    strategy_name: str = Field(
        description="Strategy identifier: BASELINE_RETRY_ONCE or AI_ORCHESTRATOR"
    )
    total_revenue_at_risk: float = Field(ge=0, description="Total INR value of payment failures")
    total_recovered_revenue: float = Field(ge=0, description="Total INR successfully recovered")
    recovery_rate_percent: float = Field(
        ge=0.0, le=100.0, description="Percentage of revenue recovered"
    )
    total_cost: float = Field(ge=0, description="Total cost in INR (incentives + communication)")
    net_roi_percent: float = Field(
        description="Net ROI percentage ((Recovered - Cost) / At Risk * 100)"
    )
    cases_count: int = Field(ge=0, description="Total count of cases processed")
    recovered_cases_count: int = Field(ge=0, description="Count of successfully recovered cases")
    escalated_cases_count: int = Field(ge=0, description="Count of cases escalated to human review")
    rejected_actions_count: int = Field(
        ge=0, description="Count of actions blocked by policy engine"
    )


class BaselineComparisonResult(BaseModel):
    """Comparative analysis between naive baseline and AI orchestrator."""

    baseline: StrategyMetrics
    ai_orchestrator: StrategyMetrics
    uplift_inr: float = Field(description="Net additional revenue recovered by AI over baseline")
    uplift_percent: float = Field(description="Percentage improvement in recovery rate")
    key_findings: list[str] = Field(
        description="Executive takeaways derived from simulation results"
    )
