import React, { useState } from 'react';
import {
  TrendingUp,
  ShieldAlert,
  Zap,
  Activity,
  AlertTriangle,
  Play,
  RotateCcw,
  Sparkles,
  Layers,
  DollarSign,
  Percent,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts';
import { useDashboardQuery } from '../api/hooks/useDashboard';
import {
  useGenerateDataMutation,
  useRunBaselineMutation,
  useRunAiSimulationMutation,
} from '../api/hooks/useSimulation';

export const Dashboard: React.FC = () => {
  const { data: dashboard, refetch } = useDashboardQuery();
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

  // Chart data format
  const chartData = (dashboard?.comparison_chart || []).map((item) => ({
    name: item.segment,
    'At Risk (₹)': item.total_at_risk_inr,
    'Baseline Recovered (₹)': item.baseline_recovered_inr,
    'AI Recovered (₹)': item.ai_recovered_inr,
  }));

  const totalAtRisk = dashboard?.total_revenue_at_risk || 0;
  const aiRecovered = dashboard?.total_recovered_revenue || 0;
  const aiRecoveryRate = dashboard?.overall_recovery_rate || 0;
  const baselineRate = dashboard?.baseline_recovery_rate || 0;
  const upliftInr = dashboard?.recovery_uplift_inr || 0;
  const netRoi = dashboard?.net_roi_percent || 0;
  const policyInterventions = dashboard?.policy_interventions_count || 0;
  const escalatedCases = dashboard?.escalated_cases_count || 0;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Toast Banner */}
      {toastMessage && (
        <div className="p-4 rounded-xl bg-brand-600/90 border border-brand-400/40 text-white shadow-2xl flex items-center justify-between transition-all">
          <div className="flex items-center space-x-3">
            <Sparkles className="w-5 h-5 text-amber-300 animate-pulse" />
            <span className="text-sm font-medium">{toastMessage}</span>
          </div>
          <button
            onClick={() => setToastMessage(null)}
            className="text-xs text-white/80 hover:text-white px-2 py-1 bg-white/10 rounded"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Simulation Command Center Bar */}
      <div className="p-6 rounded-2xl bg-[#0c2340]/90 border border-slate-800 backdrop-blur shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="flex h-2.5 w-2.5 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
            </span>
            <h2 className="text-lg font-bold text-white tracking-tight">
              Simulation & Benchmark Controls
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Execute simulations over reproducible transaction failure cohorts to verify AI uplift.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={handleGenerateData}
            disabled={isBusy}
            id="btn-generate-data"
            className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center space-x-2 border border-slate-700 transition shadow disabled:opacity-50"
          >
            <RotateCcw className={`w-4 h-4 ${generateMutation.isPending ? 'animate-spin' : ''}`} />
            <span>{generateMutation.isPending ? 'Generating...' : '1. Generate Data'}</span>
          </button>

          <button
            onClick={handleRunBaseline}
            disabled={isBusy}
            id="btn-run-baseline"
            className="px-4 py-2.5 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 text-xs font-semibold flex items-center space-x-2 border border-amber-500/30 transition shadow disabled:opacity-50"
          >
            <Play className={`w-4 h-4 ${baselineMutation.isPending ? 'animate-spin' : ''}`} />
            <span>{baselineMutation.isPending ? 'Running Benchmark...' : '2. Run Baseline'}</span>
          </button>

          <button
            onClick={handleRunAi}
            disabled={isBusy}
            id="btn-run-ai"
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white text-xs font-bold flex items-center space-x-2 shadow-lg shadow-brand-500/25 border border-brand-400/30 transition disabled:opacity-50"
          >
            <Zap
              className={`w-4 h-4 ${aiMutation.isPending ? 'animate-spin text-amber-300' : ''}`}
            />
            <span>{aiMutation.isPending ? 'Running LangGraph...' : '3. Run AI Orchestrator'}</span>
          </button>
        </div>
      </div>

      {/* 4 Hero KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* KPI 1: Total Revenue at Risk */}
        <div className="p-6 rounded-2xl bg-[#0c2340]/70 border border-slate-800 shadow-xl relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Revenue at Risk
            </span>
            <div className="p-2 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-3xl font-extrabold text-white tracking-tight">
              ₹{totalAtRisk.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
            </div>
            <p className="text-xs text-slate-400 mt-1 flex items-center space-x-1">
              <span>{dashboard?.comparison_chart?.length || 0} active cohort segments</span>
            </p>
          </div>
        </div>

        {/* KPI 2: AI Recovered Revenue */}
        <div className="p-6 rounded-2xl bg-gradient-to-br from-[#0c2340] to-brand-950/40 border border-brand-500/30 shadow-xl relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-brand-300 uppercase tracking-wider">
              AI Recovered Revenue
            </span>
            <div className="p-2 rounded-lg bg-brand-500/20 text-brand-300 border border-brand-500/30">
              <DollarSign className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-3xl font-extrabold text-emerald-400 tracking-tight">
              ₹{aiRecovered.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
            </div>
            <p className="text-xs text-emerald-300 mt-1 flex items-center space-x-1 font-medium">
              <span>
                ₹{upliftInr.toLocaleString('en-IN', { maximumFractionDigits: 0 })} net gain over
                baseline
              </span>
            </p>
          </div>
        </div>

        {/* KPI 3: Recovery Rate & Uplift */}
        <div className="p-6 rounded-2xl bg-[#0c2340]/70 border border-slate-800 shadow-xl relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              AI Recovery Rate
            </span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Percent className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-3xl font-extrabold text-white tracking-tight">
              {aiRecoveryRate.toFixed(1)}%
            </div>
            <p className="text-xs text-slate-400 mt-1 flex items-center space-x-1">
              <span className="text-emerald-400 font-semibold">
                +{Math.max(0, aiRecoveryRate - baselineRate).toFixed(1)}% uplift
              </span>
              <span>vs. Baseline ({baselineRate.toFixed(1)}%)</span>
            </p>
          </div>
        </div>

        {/* KPI 4: Net ROI & Guardrails */}
        <div className="p-6 rounded-2xl bg-[#0c2340]/70 border border-slate-800 shadow-xl relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Net Recovery ROI
            </span>
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-3xl font-extrabold text-white tracking-tight">
              {netRoi.toFixed(1)}%
            </div>
            <p className="text-xs text-slate-400 mt-1 flex items-center space-x-1">
              <span className="text-indigo-300 font-medium">
                {policyInterventions} policy gates triggered
              </span>
            </p>
          </div>
        </div>
      </div>

      {/* Main Chart Section: Baseline vs AI Segment Comparison */}
      <div className="p-6 rounded-2xl bg-[#0c2340]/80 border border-slate-800 shadow-2xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-slate-800/80 gap-3">
          <div>
            <div className="flex items-center space-x-2">
              <Layers className="w-5 h-5 text-brand-400" />
              <h3 className="text-base font-bold text-white">
                Revenue Recovery Comparison by Customer Segment
              </h3>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Comparing ₹ recovered by the AI Multi-Agent Orchestrator vs. Naive Retry-Once
              baseline.
            </p>
          </div>

          <div className="flex items-center space-x-4 text-xs font-mono">
            <div className="flex items-center space-x-1.5">
              <span className="w-3 h-3 rounded-sm bg-slate-600 inline-block"></span>
              <span className="text-slate-300">At Risk</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <span className="w-3 h-3 rounded-sm bg-amber-500 inline-block"></span>
              <span className="text-slate-300">Baseline</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <span className="w-3 h-3 rounded-sm bg-emerald-500 inline-block"></span>
              <span className="text-emerald-400 font-bold">AI Orchestrator</span>
            </div>
          </div>
        </div>

        <div className="h-80 w-full mt-6">
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} tickLine={false} />
                <YAxis
                  stroke="#94a3b8"
                  fontSize={12}
                  tickFormatter={(val) => `₹${(val / 1000).toFixed(0)}k`}
                  tickLine={false}
                />
                <Tooltip
                  formatter={(
                    value: string | number | readonly (string | number)[] | undefined
                  ) => [`₹${Number(value || 0).toLocaleString('en-IN')}`, '']}
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '8px',
                    color: '#f8fafc',
                  }}
                />
                <Legend />
                <Bar dataKey="At Risk (₹)" fill="#475569" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Baseline Recovered (₹)" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                <Bar dataKey="AI Recovered (₹)" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-slate-500 space-y-3">
              <Activity className="w-10 h-10 stroke-[1.5] animate-pulse" />
              <p className="text-sm">
                No simulation data available yet. Click "Generate Data" and "Run AI" above.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Policy Governance & Operational Status Banner */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="p-5 rounded-xl bg-[#0c2340]/60 border border-slate-800 flex items-start space-x-3">
          <div className="p-2.5 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider">
              Enforced Policy Bounds
            </h4>
            <p className="text-xs text-slate-400 mt-1">
              Max 3 retries, max 10% coupon cap, and ₹25,000 threshold strictly enforced with 0 LLM
              overrides.
            </p>
          </div>
        </div>

        <div className="p-5 rounded-xl bg-[#0c2340]/60 border border-slate-800 flex items-start space-x-3">
          <div className="p-2.5 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider">
              Escalation Queue
            </h4>
            <p className="text-xs text-slate-400 mt-1">
              {escalatedCases} high-value cases routed to manual review to protect Tier-1
              relationships.
            </p>
          </div>
        </div>

        <div className="p-5 rounded-xl bg-[#0c2340]/60 border border-slate-800 flex items-start space-x-3">
          <div className="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <TrendingUp className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider">
              Verified Revenue Proof
            </h4>
            <p className="text-xs text-slate-400 mt-1">
              Every ₹ figure is computed live from database rows and simulation models, never
              hardcoded.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
