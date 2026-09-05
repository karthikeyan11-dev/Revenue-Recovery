from pydantic import BaseModel


class AnalyticsKpiSummary(BaseModel):
    total_revenue_at_risk: float = 0.0
    total_recovered_revenue: float = 0.0
    recovered_revenue_change_percent: float = 12.4
    baseline_recovered_revenue: float = 0.0
    recovery_uplift_inr: float = 0.0
    recovery_rate_percent: float = 0.0
    recovery_success_rate_percent: float = 0.0
    recovery_success_rate_change_percent: float = 8.5
    baseline_recovery_rate: float = 0.0
    rate_uplift_percent: float = 0.0
    total_recovery_cost: float = 0.0
    net_roi_percent: float = 0.0
    policy_gates_triggered: int = 0
    avg_recovery_time_hours: float = 0.0
    avg_recovery_time_change_percent: float = 1.2
    avg_recovery_time_formatted: str = "0h 0m"
    total_cases_analyzed: int = 0
    active_cases_count: int = 0
    active_cases_change_percent: int = 15


class FailureReasonBreakdownItem(BaseModel):
    failure_reason: str
    display_name: str
    reason: str = ""
    cases_count: int
    recovered_inr: float
    recovered_amount: float = 0.0
    recovery_rate_percent: float
    percentage_of_total: float = 0.0
    percentage: float = 0.0


class TopActionBreakdownItem(BaseModel):
    action: str
    action_type: str
    type: str = ""
    success_rate_percent: float
    recovered_inr: float
    recovered_amount: float = 0.0
    attempts_count: int
    attempts: int = 0


class TimeToRecoverBucketItem(BaseModel):
    bucket: str
    cases_count: int
    count: int = 0
    recovered_inr: float
    recovery_rate_percent: float
    percentage: float = 0.0


class SegmentComparisonItem(BaseModel):
    segment: str
    display_name: str
    ai_recovered_inr: float
    ai_recovered_amount: float = 0.0
    baseline_recovered_inr: float
    baseline_amount: float = 0.0
    at_risk_inr: float
    at_risk_amount: float = 0.0
    ai_recovery_rate: float
    recovery_rate_percent: float = 0.0
    baseline_recovery_rate: float


class TrendDataPoint(BaseModel):
    date: str
    ai_recovered_inr: float
    recovered: float = 0.0
    baseline_recovered_inr: float
    at_risk: float = 0.0


class PerformanceHighlights(BaseModel):
    ai_extra_revenue: float = 0.0
    recovery_rate_uplift: float = 0.0
    high_value_recovered: float = 0.0
    high_value_recovered_percent: float = 0.0
    top_performing_action: str = "Payment Link (UPI)"
    top_performing_action_rate: float = 0.0
    highest_recovery_segment: str = "High Value"
    most_effective_action: str = "WhatsApp Interactive Link"
    top_failure_reason: str = "Insufficient Funds"
    avg_recovery_turnaround_hours: float = 4.2


class AnalyticsBreakdownResponse(BaseModel):
    kpis: AnalyticsKpiSummary
    trend_over_time: list[TrendDataPoint]
    recovery_trends: list[TrendDataPoint] = []
    failure_reasons: list[FailureReasonBreakdownItem]
    customer_segments: list[SegmentComparisonItem]
    segment_breakdown: list[SegmentComparisonItem] = []
    top_actions: list[TopActionBreakdownItem]
    time_to_recover_buckets: list[TimeToRecoverBucketItem]
    performance_highlights: PerformanceHighlights
    highlights: PerformanceHighlights | None = None
