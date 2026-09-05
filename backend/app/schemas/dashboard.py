from pydantic import BaseModel, Field

from app.schemas.analyst import StrategyMetrics


class RecoveryComparisonChartItem(BaseModel):
    segment: str = Field(description="Customer cohort or leak category")
    baseline_recovered_inr: float = Field(description="INR recovered under baseline")
    ai_recovered_inr: float = Field(description="INR recovered under AI orchestrator")
    total_at_risk_inr: float = Field(description="Total at-risk revenue")


class SegmentDistributionItem(BaseModel):
    segment: str
    percentage: float
    recovered_inr: float


class TopActionSummaryItem(BaseModel):
    action: str
    action_type: str
    success_rate_percent: float
    attempts_count: int
    recovered_inr: float


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
    baseline_recovered_revenue: float = Field(default=0.0, description="Baseline recovered INR")
    recovery_uplift_inr: float = Field(description="Net additional INR won over baseline")
    rate_uplift_percent: float = Field(default=0.0, description="Recovery rate uplift %")
    active_cases_count: int = Field(ge=0, description="Open and In-Progress recovery cases")
    escalated_cases_count: int = Field(ge=0, description="Cases requiring human attention")
    policy_interventions_count: int = Field(
        ge=0, description="Actions blocked or modified by policy gate"
    )
    active_cohort_segments_count: int = Field(
        default=6, description="Number of active customer cohort segments"
    )
    total_cases_analyzed: int = Field(
        default=0, description="Total failed transaction cases in cohort"
    )
    ai_recovered_cases_count: int = Field(
        default=0, description="Number of cases recovered by AI"
    )
    ai_case_recovery_rate_percent: float = Field(
        default=0.0, description="AI case recovery success rate %"
    )
    baseline_recovered_cases_count: int = Field(
        default=0, description="Number of cases recovered by baseline"
    )
    baseline_case_recovery_rate_percent: float = Field(
        default=0.0, description="Baseline case recovery success rate %"
    )
    case_recovery_uplift_count: int = Field(
        default=0, description="Net extra cases recovered by AI over baseline"
    )
    case_recovery_uplift_percent: float = Field(
        default=0.0, description="Net case recovery rate % uplift"
    )
    comparison_chart: list[RecoveryComparisonChartItem] = Field(
        default=[], description="Segment-by-segment comparison"
    )
    segment_distribution: list[SegmentDistributionItem] = Field(
        default=[], description="Segment percentage distribution of recovered revenue"
    )
    top_actions: list[TopActionSummaryItem] = Field(
        default=[], description="Top AI recovery actions with success rates"
    )
    baseline_summary: StrategyMetrics | None = None
    ai_summary: StrategyMetrics | None = None


class StrategyComparisonSummary(BaseModel):
    total_at_risk: float = Field(ge=0)
    total_recovered: float = Field(ge=0)
    recovery_rate_percent: float = Field(ge=0)
    total_cost: float = Field(ge=0)
    net_roi_percent: float = Field(default=0.0)
    cases_count: int = Field(ge=0)
    recovered_cases_count: int = Field(ge=0)
    case_recovery_rate_percent: float = Field(default=0.0)


class UpliftMetrics(BaseModel):
    extra_revenue_recovered_inr: float
    recovery_rate_uplift_percent: float
    net_roi_percent: float
    extra_cases_recovered: int = Field(default=0)
    case_recovery_rate_uplift_percent: float = Field(default=0.0)


class DashboardComparisonResponse(BaseModel):
    baseline: StrategyComparisonSummary
    ai: StrategyComparisonSummary
    uplift: UpliftMetrics
    key_findings: list[str] = Field(default=[])


class DiagnosticMetricsPayload(BaseModel):
    total_at_risk: float
    ai_recovered: float
    ai_recovery_rate: float
    baseline_recovered: float
    baseline_recovery_rate: float
    rev_diff_inr: float
    rev_rate_diff_percent: float
    total_cases: int
    ai_recovered_cases: int
    ai_case_rate: float
    baseline_recovered_cases: int
    baseline_case_rate: float
    case_diff_count: int
    case_rate_diff_percent: float
    escalated_cases_count: int
    escalated_revenue_inr: float


class EscalatedCaseSummary(BaseModel):
    case_id: str
    amount: float
    failure_reason: str
    policy_rule: str
    reasoning: str


class RecoveryDiagnosticResponse(BaseModel):
    verdict: str  # "AI_AHEAD" | "BASELINE_AHEAD" | "BALANCED"
    headline: str
    summary: str
    primary_reasons: list[str]
    metrics: DiagnosticMetricsPayload
    escalated_cases: list[EscalatedCaseSummary] = Field(default=[])
    recommendation: str
    generated_at: str
    llm_reasoning_status: str = Field(default="live", description="'live', 'cached', or 'unavailable'")
    real_model_attribution: str | None = Field(
        default=None, description="Actual model and provider name used for generation"
    )
    cohort_run_id: str = Field(default="", description="Unique fingerprint of this cohort batch")


