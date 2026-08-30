import React from 'react';
import { AlertCircle, CheckCircle2, TrendingUp, ShieldCheck } from 'lucide-react';
import { Card, CardContent } from '../../../components/ui/card';
import { formatCurrency, formatPercent } from '../../../lib/utils';
import { DASHBOARD_CONSTANTS } from '../constants/dashboard.constants';
import type { DashboardKpiCardsProps } from '../types/dashboard.types';

export const DashboardKpiCards: React.FC<DashboardKpiCardsProps> = ({ metrics }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
      {/* 1. Revenue at Risk */}
      <Card className="bg-white border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
        <CardContent className="p-5">
          <div className="flex items-start justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              {DASHBOARD_CONSTANTS.KPI_TITLES.REVENUE_AT_RISK}
            </span>
            <div className="w-8 h-8 rounded-lg bg-rose-50 flex items-center justify-center text-rose-600">
              <AlertCircle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-slate-900 tracking-tight">
              {formatCurrency(metrics.total_revenue_at_risk)}
            </div>
            <p className="text-xs text-slate-500 mt-1 flex items-center font-medium">
              {metrics.active_cohort_segments_count} active cohort segments
            </p>
          </div>
        </CardContent>
      </Card>

      {/* 2. AI Recovered Revenue */}
      <Card className="bg-white border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
        <CardContent className="p-5">
          <div className="flex items-start justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              {DASHBOARD_CONSTANTS.KPI_TITLES.AI_RECOVERED}
            </span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 flex items-center justify-center text-emerald-600">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-slate-900 tracking-tight">
              {formatCurrency(metrics.total_recovered_revenue)}
            </div>
            <p className="text-xs text-emerald-600 mt-1 flex items-center font-medium">
              <span className="font-semibold mr-1">↑</span>
              {formatCurrency(metrics.recovery_uplift_inr)} vs. baseline
            </p>
          </div>
        </CardContent>
      </Card>

      {/* 3. AI Recovery Rate */}
      <Card className="bg-white border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
        <CardContent className="p-5">
          <div className="flex items-start justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              {DASHBOARD_CONSTANTS.KPI_TITLES.AI_RECOVERY_RATE}
            </span>
            <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-slate-900 tracking-tight">
              {formatPercent(metrics.overall_recovery_rate)}
            </div>
            <p className="text-xs text-emerald-600 mt-1 flex items-center font-medium">
              <span className="font-semibold mr-1">↑</span>
              {formatPercent(metrics.rate_uplift_percent)} vs. baseline (
              {formatPercent(metrics.baseline_recovery_rate)})
            </p>
          </div>
        </CardContent>
      </Card>

      {/* 4. Net Recovery ROI */}
      <Card className="bg-white border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
        <CardContent className="p-5">
          <div className="flex items-start justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              {DASHBOARD_CONSTANTS.KPI_TITLES.NET_ROI}
            </span>
            <div className="w-8 h-8 rounded-lg bg-purple-50 flex items-center justify-center text-purple-600">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-slate-900 tracking-tight">
              {formatPercent(metrics.net_roi_percent)}
            </div>
            <p className="text-xs text-purple-600 mt-1 flex items-center font-medium">
              {metrics.policy_interventions_count} policy gates triggered
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
