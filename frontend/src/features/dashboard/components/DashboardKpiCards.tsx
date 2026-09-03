import React from 'react';
import {
  AlertCircle,
  CheckCircle2,
  TrendingUp,
  ShieldCheck,
  RefreshCw,
  FileText,
  Clock,
  Trophy,
} from 'lucide-react';
import { Card, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { formatCurrency, formatPercent } from '../../../lib/utils';
import type { DashboardKpiCardsProps } from '../types/dashboard.types';

export const DashboardKpiCards: React.FC<DashboardKpiCardsProps> = ({ metrics }) => {
  // Financial Revenue Values & Diffs
  const totalRevenue = metrics.total_revenue_at_risk || 0;
  const aiRevenue = metrics.total_recovered_revenue || 0;
  const aiRevenueRate = metrics.overall_recovery_rate || 0;
  const baseRevenue = metrics.baseline_recovered_revenue || 0;
  const baseRevenueRate = metrics.baseline_recovery_rate || 0;
  const revDiffInr = aiRevenue - baseRevenue;
  const revRateDiffPercent = aiRevenueRate - baseRevenueRate;

  // Case Resolution Values & Diffs
  const totalCases = metrics.total_cases_analyzed || 25;
  const aiCases = metrics.ai_recovered_cases_count || 0;
  const aiCaseRate = metrics.ai_case_recovery_rate_percent || 0;
  const baseCases = metrics.baseline_recovered_cases_count || 0;
  const baseCaseRate = metrics.baseline_case_recovery_rate_percent || 0;
  const caseDiffCount = aiCases - baseCases;
  const caseRateDiffPercent = aiCaseRate - baseCaseRate;

  return (
    <div className="space-y-4">
      {/* SECTION 1: FINANCIAL REVENUE IMPACT */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
            <TrendingUp className="w-3.5 h-3.5 text-blue-600" />
            Financial Revenue Impact (Money Measured)
          </span>
          <span className="text-[11px] text-slate-400 font-medium">
            Gross INR Recovery & Benchmark Comparison
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* 1. Total Revenue at Risk */}
          <Card className="bg-white border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-4 sm:p-5">
              <div className="flex items-start justify-between">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Total Revenue at Risk
                </span>
                <div className="w-8 h-8 rounded-lg bg-rose-50 flex items-center justify-center text-rose-600">
                  <AlertCircle className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-3">
                <div className="text-2xl font-bold text-slate-900 tracking-tight">
                  {formatCurrency(totalRevenue)}
                </div>
                <p className="text-xs text-slate-500 mt-1 font-medium">
                  Across {metrics.active_cohort_segments_count} failure categories in active cohort
                </p>
              </div>
            </CardContent>
          </Card>

          {/* 2. AI Recovered Revenue (with exact Diff vs Baseline) */}
          <Card className="bg-white border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-4 sm:p-5">
              <div className="flex items-start justify-between">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  AI Recovered Revenue
                </span>
                <div className="w-8 h-8 rounded-lg bg-emerald-50 flex items-center justify-center text-emerald-600">
                  <CheckCircle2 className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-3">
                <div className="flex items-baseline gap-2">
                  <span className="text-2xl font-bold text-emerald-700 tracking-tight">
                    {formatCurrency(aiRevenue)}
                  </span>
                  <Badge
                    variant="outline"
                    className={`text-[11px] font-bold ${
                      revDiffInr >= 0
                        ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                        : 'bg-amber-50 text-amber-700 border-amber-200'
                    }`}
                  >
                    {revDiffInr >= 0 ? `+${formatCurrency(revDiffInr)}` : `-${formatCurrency(Math.abs(revDiffInr))}`} Diff
                  </Badge>
                </div>
                <div className="mt-1 flex flex-wrap items-center gap-x-1.5 text-xs">
                  <span className="font-semibold text-slate-700">{formatPercent(aiRevenueRate)} rate</span>
                  <span className="text-slate-400">•</span>
                  <span className={`font-semibold ${revRateDiffPercent >= 0 ? 'text-emerald-600' : 'text-amber-600'}`}>
                    {revRateDiffPercent >= 0 ? `+${formatPercent(revRateDiffPercent)}` : `${formatPercent(revRateDiffPercent)}`} rate diff
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 3. Baseline Recovered Revenue */}
          <Card className="bg-white border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-4 sm:p-5">
              <div className="flex items-start justify-between">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Baseline Recovered
                </span>
                <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center text-slate-600">
                  <RefreshCw className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-3">
                <div className="text-2xl font-bold text-slate-800 tracking-tight">
                  {formatCurrency(baseRevenue)}
                </div>
                <p className="text-xs text-slate-500 mt-1 font-medium flex items-center gap-1">
                  <span className="font-semibold text-slate-700">{formatPercent(baseRevenueRate)}</span>
                  <span>passive 24h blind retry rate</span>
                </p>
              </div>
            </CardContent>
          </Card>

          {/* 4. Net Recovery ROI & Net Uplift */}
          <Card className="bg-white border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-4 sm:p-5">
              <div className="flex items-start justify-between">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Net Recovery ROI
                </span>
                <div className="w-8 h-8 rounded-lg bg-purple-50 flex items-center justify-center text-purple-600">
                  <ShieldCheck className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-3">
                <div className="flex items-baseline gap-2">
                  <span className="text-2xl font-bold text-slate-900 tracking-tight">
                    {formatPercent(metrics.net_roi_percent)}
                  </span>
                  <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200 text-[11px] font-bold">
                    Net Margin
                  </Badge>
                </div>
                <p className="text-xs text-purple-700 mt-1 font-semibold">
                  {revDiffInr >= 0 ? `+${formatCurrency(revDiffInr)}` : `-${formatCurrency(Math.abs(revDiffInr))}`} net margin ({metrics.policy_interventions_count} policy gates)
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* SECTION 2: CASE RESOLUTION & WIN RATES */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
            <FileText className="w-3.5 h-3.5 text-emerald-600" />
            Case Resolution & Volume (Cases Won vs. Lost)
          </span>
          <span className="text-[11px] text-slate-400 font-medium">
            Customer Account Recovery Count & Comparative Win Rate
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* 5. Total Cases Evaluated */}
          <Card className="bg-white border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-4 sm:p-5">
              <div className="flex items-start justify-between">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Total Cases Evaluated
                </span>
                <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600">
                  <FileText className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-3">
                <div className="text-2xl font-bold text-slate-900 tracking-tight">
                  {totalCases} Cases
                </div>
                <p className="text-xs text-slate-500 mt-1 font-medium">
                  Full transaction failure cohort evaluated
                </p>
              </div>
            </CardContent>
          </Card>

          {/* 6. AI Cases Recovered (with exact Diff vs Baseline) */}
          <Card className="bg-white border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-4 sm:p-5">
              <div className="flex items-start justify-between">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  AI Cases Recovered
                </span>
                <div className="w-8 h-8 rounded-lg bg-emerald-50 flex items-center justify-center text-emerald-600">
                  <CheckCircle2 className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-3">
                <div className="flex items-baseline gap-2">
                  <span className="text-2xl font-bold text-emerald-700 tracking-tight">
                    {aiCases} Cases
                  </span>
                  <Badge
                    variant="outline"
                    className={`text-[11px] font-bold ${
                      caseDiffCount >= 0
                        ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                        : 'bg-rose-50 text-rose-700 border-rose-200'
                    }`}
                  >
                    {caseDiffCount >= 0 ? `+${caseDiffCount}` : `${caseDiffCount}`} vs Base
                  </Badge>
                </div>
                <div className="mt-1 flex flex-wrap items-center gap-x-1.5 text-xs">
                  <span className="font-semibold text-emerald-700">{formatPercent(aiCaseRate)} win rate</span>
                  <span className="text-slate-400">•</span>
                  <span className={`font-semibold ${caseRateDiffPercent >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                    {caseRateDiffPercent >= 0 ? `+${formatPercent(caseRateDiffPercent)}` : `${formatPercent(caseRateDiffPercent)}`} rate diff
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 7. Baseline Cases Recovered */}
          <Card className="bg-white border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-4 sm:p-5">
              <div className="flex items-start justify-between">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Baseline Cases Recovered
                </span>
                <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center text-slate-600">
                  <Clock className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-3">
                <div className="flex items-baseline gap-2">
                  <span className="text-2xl font-bold text-slate-700 tracking-tight">
                    {baseCases} Cases
                  </span>
                  <Badge variant="secondary" className="bg-slate-100 text-slate-700 text-[11px] font-semibold">
                    {formatPercent(baseCaseRate)} Rate
                  </Badge>
                </div>
                <p className="text-xs text-slate-500 mt-1 font-medium">
                  {baseCases} of {totalCases} accounts recovered via blind retry
                </p>
              </div>
            </CardContent>
          </Card>

          {/* 8. Net Cases Won (AI Lead) */}
          <Card className="bg-gradient-to-br from-emerald-50/60 to-white border-emerald-200/80 shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-4 sm:p-5">
              <div className="flex items-start justify-between">
                <span className="text-xs font-bold text-emerald-900 uppercase tracking-wider">
                  Net Cases Won (AI Lead)
                </span>
                <div className="w-8 h-8 rounded-lg bg-emerald-100 flex items-center justify-center text-emerald-700">
                  <Trophy className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-3">
                <div className="flex items-baseline gap-2">
                  <span className="text-2xl font-bold text-emerald-700 tracking-tight">
                    {caseDiffCount >= 0 ? `+${caseDiffCount}` : `${caseDiffCount}`} Cases
                  </span>
                  <Badge variant="outline" className="bg-emerald-100 text-emerald-800 border-emerald-300 text-[11px] font-bold">
                    {caseRateDiffPercent >= 0 ? `+${formatPercent(caseRateDiffPercent)}` : `${formatPercent(caseRateDiffPercent)}`} Lead
                  </Badge>
                </div>
                <p className="text-xs text-emerald-800 mt-1 font-medium">
                  AI resolved {caseDiffCount > 0 ? caseDiffCount : 0} extra accounts over passive baseline
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
