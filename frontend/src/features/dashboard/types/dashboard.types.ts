import type { DashboardMetricsResponse, RecoveryCaseSummaryItem } from '../../../types/api.types';

export interface DashboardContainerProps {
  timeRange?: string;
  onNavigateToCases?: () => void;
  onNavigateToSimulations?: () => void;
}

export interface DashboardKpiCardsProps {
  metrics: DashboardMetricsResponse;
}

export interface DashboardBaselineBannerProps {
  metrics: DashboardMetricsResponse;
  onViewDetails?: () => void;
  onDismiss?: () => void;
}

export interface DashboardSegmentComparisonChartProps {
  data: DashboardMetricsResponse['comparison_chart'];
}

export interface DashboardSegmentDonutChartProps {
  data: DashboardMetricsResponse['segment_distribution'];
}

export interface DashboardRecentCasesTableProps {
  cases: RecoveryCaseSummaryItem[];
  onViewAll?: () => void;
}

export interface DashboardTopActionsTableProps {
  actions: DashboardMetricsResponse['top_actions'];
}
