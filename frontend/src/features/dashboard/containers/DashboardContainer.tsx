import React from 'react';
import { RefreshCw, AlertTriangle } from 'lucide-react';
import { Button } from '../../../components/ui/button';
import { DashboardKpiCards } from '../components/DashboardKpiCards';
import { DashboardSimulationControls } from '../components/DashboardSimulationControls';
import { DashboardComparisonCard } from '../components/DashboardComparisonCard';
import { DashboardRecentCasesTable } from '../components/DashboardRecentCasesTable';
import { DashboardSegmentComparisonChart } from '../components/DashboardSegmentComparisonChart';
import { DashboardSegmentDonutChart } from '../components/DashboardSegmentDonutChart';
import { DashboardTopActionsTable } from '../components/DashboardTopActionsTable';
import { useGetDashboardSummary } from '../hooks/useGetDashboardSummary';
import { LogoLoader } from '../../../components/common/LogoLoader';
import type { DashboardContainerProps } from '../types/dashboard.types';

export const DashboardContainer: React.FC<DashboardContainerProps> = ({
  timeRange,
  onNavigateToCases,
}) => {
  const { metrics, recentCases, isLoading, isError, error, refetch } = useGetDashboardSummary(timeRange);

  if (isLoading) {
    return <LogoLoader variant="dashboard" label="Aggregating live cohort telemetry..." />;
  }

  if (isError || !metrics) {
    return (
      <div className="p-8 bg-white border border-rose-200 rounded-xl shadow-sm text-center space-y-4">
        <div className="w-12 h-12 rounded-full bg-rose-50 text-rose-600 flex items-center justify-center mx-auto">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <div className="text-base font-semibold text-slate-900">Failed to load Dashboard data</div>
        <p className="text-xs text-slate-500 max-w-md mx-auto">
          {(error as Error)?.message || 'An unexpected error occurred while communicating with the backend.'}
        </p>
        <Button onClick={() => refetch()} variant="outline" size="sm" className="space-x-2">
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Retry Connection</span>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 1. Interactive Batch Simulation & Cohort Data Seeder */}
      <DashboardSimulationControls onSimulationCompleted={() => refetch()} />

      {/* 2. Headline KPI Cards */}
      <DashboardKpiCards metrics={metrics} />

      {/* 3. Baseline vs AI Comparative Strategy Evaluation */}
      <DashboardComparisonCard metrics={metrics} />

      {/* 4. Full-Width Revenue Recovery Comparison by Failure Reason Chart */}
      <DashboardSegmentComparisonChart data={metrics.comparison_chart} />

      {/* 5. Failure Reason Distribution (Left) & Top Recovery Actions (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <DashboardSegmentDonutChart data={metrics.segment_distribution} />
        <DashboardTopActionsTable actions={metrics.top_actions} />
      </div>

      {/* 6. Full-Width Recent Recovery Cases Table */}
      <DashboardRecentCasesTable cases={recentCases} onViewAll={onNavigateToCases} />
    </div>
  );
};

