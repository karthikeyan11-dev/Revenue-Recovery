import type {
  DashboardMetricsResponse,
  StrategyMetrics,
  RecoveryComparisonChartItem,
  RunStrategyRequest,
  RunStrategyResponse,
  GenerateDataRequest,
  GenerateDataResponse,
} from '../api/generated';

export type {
  DashboardMetricsResponse,
  StrategyMetrics,
  RecoveryComparisonChartItem,
  RunStrategyRequest,
  RunStrategyResponse,
  GenerateDataRequest,
  GenerateDataResponse,
};

export type DashboardSummaryResponse = DashboardMetricsResponse;
export type StrategyMetricsResponse = StrategyMetrics;
export type BaselineSimulationResponse = RunStrategyResponse;
export type AISimulationResponse = RunStrategyResponse;

export interface StrategyComparisonResponse {
  baseline_metrics?: StrategyMetrics | null;
  ai_metrics?: StrategyMetrics | null;
  uplift_inr: number;
  uplift_percent: number;
  key_findings: string[];
}
