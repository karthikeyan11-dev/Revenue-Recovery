import React, { useState } from 'react';
import {
  TrendingUp,
  ShieldAlert,
  Zap,
  Play,
  RotateCcw,
  Sparkles,
  Layers,
  DollarSign,
} from 'lucide-react';
import { useDashboardSummary } from '../hooks/useDashboardSummary';
import {
  useGenerateDataMutation,
  useRunBaselineMutation,
  useRunAiSimulationMutation,
} from '../../../api/hooks/useSimulation';
import { StatCard } from '../components/StatCard';
import { RecoveryComparisonChart } from '../components/RecoveryComparisonChart';
import { MetricCard } from '../components/MetricCard';
import { ROIHero } from '../components/ROIHero';
import { Card } from '../../../components/common/Card';
import { Button } from '../../../components/common/Button';
import type { StrategyComparisonResponse } from '../../../types/metrics';

export const DashboardContainer: React.FC = () => {
  const { data: dashboard, refetch } = useDashboardSummary();
  const generateMutation = useGenerateDataMutation();
  const baselineMutation = useRunBaselineMutation();
  const aiMutation = useRunAiSimulationMutation();

  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 5000);
  };

  const handleGenerateData = async () => {
    try {
      const res = await generateMutation.mutateAsync({
        transaction_count: 500,
        failure_rate: 0.35,
      });
      showToast(
        `✓ Seeded ${res.transactions_generated} transactions with ${res.failures_generated} payment failure events across 6 cohorts.`
      );
      refetch();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      showToast(`❌ Failed to generate data: ${msg}`);
    }
  };

  const handleRunBaseline = async () => {
    try {
      const res = await baselineMutation.mutateAsync({ limit: 200 });
      showToast(
        `✓ Naive Baseline Completed: Recovered ₹${res.metrics.total_recovered_revenue.toLocaleString(
          'en-IN'
        )} (${res.metrics.recovery_rate_percent.toFixed(1)}% recovery rate).`
      );
      refetch();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      showToast(`❌ Baseline run failed: ${msg}`);
    }
  };

  const handleRunAi = async () => {
    try {
      const res = await aiMutation.mutateAsync({ limit: 200, use_mock_llm: true });
      showToast(
        `🚀 AI Multi-Agent Orchestrator Completed: Recovered ₹${res.metrics.total_recovered_revenue.toLocaleString(
          'en-IN'
        )} (${res.metrics.recovery_rate_percent.toFixed(1)}% recovery rate).`
      );
      refetch();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      showToast(`❌ AI run failed: ${msg}`);
    }
  };

  const isBusy = generateMutation.isPending || baselineMutation.isPending || aiMutation.isPending;

  // Build comparison object if available
  const comparison: StrategyComparisonResponse | null =
    dashboard?.ai_summary && dashboard?.baseline_summary
      ? {
          baseline_metrics: dashboard.baseline_summary,
          ai_metrics: dashboard.ai_summary,
          uplift_inr: dashboard.recovery_uplift_inr || 0,
          uplift_percent:
            (dashboard.overall_recovery_rate || 0) - (dashboard.baseline_recovery_rate || 0),
          key_findings: [
            `AI orchestrator recovered ₹${(dashboard.recovery_uplift_inr || 0).toLocaleString('en-IN')} additional revenue.`,
            `Overall recovery rate reached ${(dashboard.overall_recovery_rate || 0).toFixed(1)}% vs ${(dashboard.baseline_recovery_rate || 0).toFixed(1)}% baseline.`,
            `${dashboard.policy_interventions_count || 0} deterministic policy interventions guarded brand trust.`,
          ],
        }
      : null;

  return (
    <div className="space-y-8">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="bg-brand-600/90 text-white text-xs px-4 py-3 rounded-xl shadow-xl flex items-center justify-between border border-brand-400/30 animate-in fade-in duration-200">
          <span>{toastMessage}</span>
          <button
            onClick={() => setToastMessage(null)}
            className="text-white/70 hover:text-white font-bold ml-4"
          >
            ✕
          </button>
        </div>
      )}

      {/* Hero Header & Control Center */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <TrendingUp className="h-6 w-6 text-brand-400" />
            Revenue Recovery Command Center
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Real-time multi-agent autonomous revenue leakage intervention metrics and empirical uplift comparison.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex flex-wrap items-center gap-2.5">
          <Button
            variant="secondary"
            size="sm"
            onClick={handleGenerateData}
            isLoading={generateMutation.isPending}
            disabled={isBusy}
            id="btn-generate-data"
          >
            <RotateCcw className="h-3.5 w-3.5 mr-1.5" />
            Generate Cohorts (500)
          </Button>

          <Button
            variant="secondary"
            size="sm"
            onClick={handleRunBaseline}
            isLoading={baselineMutation.isPending}
            disabled={isBusy}
            id="btn-run-baseline"
          >
            <Play className="h-3.5 w-3.5 mr-1.5 text-slate-400" />
            Run Baseline
          </Button>

          <Button
            variant="primary"
            size="sm"
            onClick={handleRunAi}
            isLoading={aiMutation.isPending}
            disabled={isBusy}
            id="btn-run-ai"
          >
            <Sparkles className="h-3.5 w-3.5 mr-1.5 text-amber-300" />
            Run AI Orchestrator
          </Button>
        </div>
      </div>

      {/* Verified AI Uplift Hero */}
      <ROIHero comparison={comparison} />

      {/* Top Level Metric KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Revenue At Risk"
          value={`₹${(dashboard?.total_revenue_at_risk || 0).toLocaleString('en-IN')}`}
          subtitle="Identified leakages"
          icon={<ShieldAlert className="h-4 w-4" />}
          iconBg="bg-rose-500/10 text-rose-400"
        />

        <StatCard
          title="Total Recovered (AI)"
          value={`₹${(dashboard?.total_recovered_revenue || 0).toLocaleString('en-IN')}`}
          subtitle={`${(dashboard?.overall_recovery_rate || 0).toFixed(1)}% recovery rate`}
          icon={<DollarSign className="h-4 w-4" />}
          iconBg="bg-emerald-500/10 text-emerald-400"
          trend={`+₹${(dashboard?.recovery_uplift_inr || 0).toLocaleString('en-IN')}`}
        />

        <StatCard
          title="Active Recovery Cases"
          value={dashboard?.active_cases_count || 0}
          subtitle={`${dashboard?.escalated_cases_count || 0} requiring human review`}
          icon={<Layers className="h-4 w-4" />}
          iconBg="bg-brand-500/10 text-brand-400"
        />

        <StatCard
          title="Policy Interventions"
          value={dashboard?.policy_interventions_count || 0}
          subtitle="Gated or Modified Actions"
          icon={<Zap className="h-4 w-4" />}
          iconBg="bg-amber-500/10 text-amber-400"
        />
      </div>

      {/* Side-by-Side Strategy Comparison Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <MetricCard
          title="Naive Baseline Strategy (Single Retry)"
          metrics={dashboard?.baseline_summary}
          badge="CONTROL GROUP"
          accentColor="border-slate-800"
        />

        <MetricCard
          title="AI Orchestrator (Multi-Agent + Contextual Policy)"
          metrics={dashboard?.ai_summary}
          badge="AI EXPERIMENT"
          accentColor="border-brand-500/40 bg-gradient-to-b from-[#0c2340]/90 to-brand-950/20"
        />
      </div>

      {/* Cohort Recovery Performance Chart */}
      <Card
        title="Cohort Recovery Performance: Baseline vs AI Orchestrator"
        subtitle="Breakdown of ₹ At Risk, Baseline Recovered, and AI Recovered by Customer Segment"
      >
        <RecoveryComparisonChart
          data={(dashboard?.comparison_chart || []).map((item) => ({
            segment: item.segment,
            total_at_risk_inr: item.total_at_risk_inr,
            baseline_recovered_inr: item.baseline_recovered_inr,
            ai_recovered_inr: item.ai_recovered_inr,
          }))}
        />
      </Card>
    </div>
  );
};
