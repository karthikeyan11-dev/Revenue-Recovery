export interface DashboardMetricsResponse {
  total_revenue_at_risk: number;
  total_recovered_revenue: number;
  overall_recovery_rate: number;
  net_roi_percent: number;
  active_cohort_segments_count: number;
  recovery_uplift_inr: number;
  baseline_recovered_revenue: number;
  baseline_recovery_rate: number;
  rate_uplift_percent: number;
  policy_interventions_count: number;
  total_cases_analyzed?: number;
  ai_recovered_cases_count?: number;
  ai_case_recovery_rate_percent?: number;
  baseline_recovered_cases_count?: number;
  baseline_case_recovery_rate_percent?: number;
  case_recovery_uplift_count?: number;
  case_recovery_uplift_percent?: number;
  comparison_chart: Array<{
    segment: string;
    total_at_risk_inr: number;
    baseline_recovered_inr: number;
    ai_recovered_inr: number;
    recovery_rate_percent?: number;
  }>;
  segment_distribution: Array<{
    segment: string;
    percentage: number;
    recovered_inr: number;
    color?: string;
  }>;
  top_actions: Array<{
    action?: string;
    action_type: string;
    type_display?: string;
    attempts_count: number;
    success_rate_percent: number;
    recovered_amount_inr?: number;
    recovered_inr?: number;
  }>;
}

export interface RecoveryCaseSummaryItem {
  id: string;
  customer_id: string;
  customer_name: string;
  customer_email: string;
  customer_segment: string;
  leak_type?: string;
  leak_amount?: number;
  amount_at_risk?: number;
  failure_reason?: string;
  failure_code?: string;
  recoverability_score?: number;
  recovered_amount: number;
  recovery_cost?: number;
  status: 'OPEN' | 'IN_PROGRESS' | 'RECOVERED' | 'FAILED' | 'ESCALATED' | 'BLOCKED';
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  recovery_rate_percent: number;
  has_sufficient_precedent?: boolean;
  precedent_count?: number;
  promise_status?: string | null;
  agents_involved: string[] | number;
  current_step?: string;
  created_at: string;
  resolved_at?: string | null;
}

export interface CasesListResponse {
  items: RecoveryCaseSummaryItem[];
  total: number;
  open_count?: number;
  in_progress_count?: number;
  recovered_count?: number;
  escalated_count?: number;
  failed_count?: number;
}

export interface RecoveryCaseDetail {
  id: string;
  customer_id: string;
  customer_name: string;
  customer_email: string;
  customer_segment: string;
  leak_type?: string;
  leak_amount?: number;
  amount_at_risk?: number;
  failure_reason?: string;
  payer_reliability_score?: number;
  failure_code?: string;
  recoverability_score?: number;
  recovered_amount: number;
  recovery_cost?: number;
  status: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  recovery_rate_percent?: number;
  has_sufficient_precedent?: boolean;
  precedent_count?: number;
  promise_status?: string | null;
  agents_involved?: string[] | number;
  current_step?: string;
  created_at: string;
  resolved_at?: string | null;
  actions: Array<{
    id: string;
    proposed_action?: string;
    action_type?: string;
    status?: string;
    cost?: number;
    policy_decision: string;
    policy_reasoning?: string | null;
    outcome?: string;
    incentive_percent?: number | null;
    executed_at?: string | null;
    success?: boolean | null;
    created_at?: string;
  }>;
  timeline: Array<{
    id?: string;
    step_name: string;
    agent: string;
    decision?: string | null;
    input_summary: string;
    output_summary: string;
    confidence: number;
    empirical_confidence?: number | null;
    llm_stated_confidence?: number | null;
    precedent_sample_size?: number | null;
    timestamp: string;
  }>;
  promises?: Array<{
    id: string;
    case_id: string;
    customer_id: string;
    customer_name: string;
    customer_email: string;
    customer_segment: string;
    committed_amount: number;
    committed_date: string;
    status: string;
    follow_up_count: number;
    created_at: string;
    resolved_at?: string | null;
  }>;
  retrieved_precedents?: Array<{
    case_id: string;
    failure_reason: string;
    action_taken: string;
    channel: string;
    outcome: string;
    recovered_amount: number;
    is_recovered: boolean;
    segment?: string | null;
  }>;
}

export interface AgentActivityItem {
  id: string;
  case_id: string;
  agent: string;
  step_name: string;
  action_name: string;
  status: 'Completed' | 'Approved' | 'Escalated' | 'Pending';
  input_summary: string;
  output_summary: string;
  decision: string;
  confidence: number;
  empirical_confidence?: number | null;
  llm_stated_confidence?: number | null;
  precedent_sample_size?: number;
  duration_seconds: number;
  timestamp: string;
}

export interface AgentStatusInfo {
  name: string;
  status: string;
  last_active: string;
}

export interface AgentActivityStats {
  active_agents_count: number;
  total_agents_count: number;
  active_cases_count: number;
  actions_today_count: number;
  success_rate_percent: number;
  avg_processing_time_seconds: number;
  playbook_precedent_count?: number;
  playbook_learned_cases_count?: number;
  agent_statuses: AgentStatusInfo[];
}

export interface AgentActivityFeedResponse {
  activities: AgentActivityItem[];
  stats: AgentActivityStats;
  total_events: number;
}

export interface FailureReasonBreakdownItem {
  failure_reason?: string;
  display_name?: string;
  reason?: string;
  cases_count: number;
  percentage?: number;
  percentage_of_total?: number;
  recovered_amount?: number;
  recovered_inr?: number;
  recovery_rate_percent?: number;
}

export interface TopActionBreakdownItem {
  action: string;
  action_type?: string;
  type?: string;
  success_rate_percent: number;
  attempts?: number;
  attempts_count?: number;
  recovered_amount?: number;
  recovered_inr?: number;
}

export interface TimeToRecoverBucketItem {
  bucket: string;
  cases_count?: number;
  count?: number;
  percentage?: number;
  recovery_rate_percent?: number;
  recovered_inr?: number;
}

export interface SegmentComparisonItem {
  segment: string;
  display_name?: string;
  at_risk_amount?: number;
  at_risk_inr?: number;
  baseline_amount?: number;
  baseline_recovered_inr?: number;
  ai_recovered_amount?: number;
  ai_recovered_inr?: number;
  recovery_rate_percent?: number;
  ai_recovery_rate?: number;
  baseline_recovery_rate?: number;
}

export interface TrendDataPoint {
  date: string;
  at_risk?: number;
  baseline_recovered_inr?: number;
  recovered?: number;
  ai_recovered_inr?: number;
}

export interface PerformanceHighlights {
  highest_recovery_segment?: string;
  most_effective_action?: string;
  top_performing_action?: string;
  top_failure_reason?: string;
  avg_recovery_turnaround_hours?: number;
  ai_extra_revenue?: number;
  recovery_rate_uplift?: number;
  high_value_recovered?: number;
  high_value_recovered_percent?: number;
  top_performing_action_rate?: number;
}

export interface AnalyticsBreakdownResponse {
  kpis: {
    total_recovered_revenue: number;
    recovered_revenue_change_percent?: number;
    recovery_success_rate_percent?: number;
    recovery_rate_percent?: number;
    recovery_success_rate_change_percent?: number;
    avg_recovery_time_hours?: number;
    avg_recovery_time_change_percent?: number;
    active_cases_count?: number;
    total_cases_analyzed?: number;
    active_cases_change_percent?: number;
    total_revenue_at_risk?: number;
    baseline_recovered_revenue?: number;
    recovery_uplift_inr?: number;
    net_roi_percent?: number;
  };
  failure_reasons: FailureReasonBreakdownItem[];
  top_actions: TopActionBreakdownItem[];
  time_to_recover_buckets: TimeToRecoverBucketItem[];
  customer_segments?: SegmentComparisonItem[];
  segment_breakdown?: SegmentComparisonItem[];
  trend_over_time?: TrendDataPoint[];
  recovery_trends?: TrendDataPoint[];
  performance_highlights?: PerformanceHighlights;
  highlights?: PerformanceHighlights;
}

export interface SimulationStepTelemetry {
  name: string;
  duration_formatted: string;
  duration_seconds: number;
  status: string;
  summary: string;
}

export interface SimulationHistoryItem {
  id: string;
  name: string;
  strategy_type: string;
  status: string;
  recovered_amount: number;
  recovery_rate_percent: number;
  total_revenue_at_risk: number;
  cases_count: number;
  step_telemetry: SimulationStepTelemetry[];
  run_at: string;
}

export interface SimulationHistoryResponse {
  simulations: SimulationHistoryItem[];
  total: number;
}

export interface StrategyMetrics {
  total_revenue_at_risk: number;
  total_recovered_revenue: number;
  recovery_rate_percent: number;
  total_cost: number;
  net_roi_percent: number;
  cases_count: number;
  recovered_cases_count: number;
  escalated_cases_count: number;
  rejected_actions_count: number;
  segment_breakdown?: Record<string, { at_risk: number; recovered: number }>;
  simulation_id?: string;
  simulation_name?: string;
  step_telemetry?: SimulationStepTelemetry[];
}

export interface RunStrategyResponse {
  simulation_id?: string;
  simulation_name?: string;
  strategy?: string;
  strategy_name?: string;
  cases_processed?: number;
  status?: string;
  metrics: StrategyMetrics;
  step_telemetry?: SimulationStepTelemetry[];
  message: string;
}

export interface CustomerSummaryItem {
  id: string;
  name: string;
  email: string;
  phone?: string | null;
  segment: string;
  risk_level: 'High' | 'Medium' | 'Low' | string;
  total_spend: number;
  recovery_rate_percent: number;
  active_cases_count: number;
  cases_count?: number;
  recovered_cases_count?: number;
  outstanding_amount?: number;
  total_recovered_amount?: number;
  status?: string;
  created_at: string;
}

export interface CustomerStatsSummary {
  total_customers: number;
  active_accounts: number;
  active_customers?: number;
  at_risk_accounts: number;
  at_risk_customers?: number;
  avg_customer_value: number;
  total_outstanding_amount?: number;
}

export interface CustomersListResponse {
  items: CustomerSummaryItem[];
  total: number;
  stats: CustomerStatsSummary;
  page: number;
  page_size: number;
}

export interface PlaybookReasonBreakdownItem {
  failure_reason: string;
  display_name: string;
  count: number;
}

export interface PlaybookActionBreakdownItem {
  action: string;
  display_name: string;
  count: number;
}

export interface PlaybookOutcomesSummary {
  recovered_count: number;
  failed_or_escalated_count: number;
}

export interface PlaybookStatsDetail {
  total_cases: number;
  baseline_precedents: number;
  learned_cases: number;
  failure_reasons: PlaybookReasonBreakdownItem[];
  outcomes?: PlaybookOutcomesSummary;
  actions: PlaybookActionBreakdownItem[];
}

export interface DiagnosticMetricsPayload {
  total_at_risk: number;
  ai_recovered: number;
  ai_recovery_rate: number;
  baseline_recovered: number;
  baseline_recovery_rate: number;
  rev_diff_inr: number;
  rev_rate_diff_percent: number;
  total_cases: number;
  ai_recovered_cases: number;
  ai_case_rate: number;
  baseline_recovered_cases: number;
  baseline_case_rate: number;
  case_diff_count: number;
  case_rate_diff_percent: number;
  escalated_cases_count: number;
  escalated_revenue_inr: number;
}

export interface EscalatedCaseSummary {
  case_id: string;
  amount: number;
  failure_reason: string;
  policy_rule: string;
  reasoning: string;
}

export interface RecoveryDiagnosticResponse {
  verdict: 'AI_AHEAD' | 'BASELINE_AHEAD' | 'BALANCED';
  headline: string;
  summary: string;
  primary_reasons: string[];
  metrics: DiagnosticMetricsPayload;
  escalated_cases: EscalatedCaseSummary[];
  recommendation: string;
  generated_at: string;
  llm_reasoning_status?: 'live' | 'cached' | 'unavailable';
  real_model_attribution?: string | null;
  cohort_run_id?: string;
}


