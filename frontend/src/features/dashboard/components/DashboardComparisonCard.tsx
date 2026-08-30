import React from 'react';
import { ArrowUpRight, Zap } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { formatCurrency, formatPercent } from '../../../lib/utils';
import type { DashboardMetricsResponse } from '../../../types/api.types';

interface DashboardComparisonCardProps {
  metrics: DashboardMetricsResponse;
}

export const DashboardComparisonCard: React.FC<DashboardComparisonCardProps> = ({ metrics }) => {
  const atRisk = metrics.total_revenue_at_risk || 0;
  const baseRecovered = metrics.baseline_recovered_revenue || 0;
  const baseRate = metrics.baseline_recovery_rate || 0;
  const aiRecovered = metrics.total_recovered_revenue || 0;
  const aiRate = metrics.overall_recovery_rate || 0;
  const upliftInr = metrics.recovery_uplift_inr || 0;
  const upliftPercent = metrics.rate_uplift_percent || 0;

  return (
    <Card className="bg-white border-slate-200/80 shadow-sm overflow-hidden">
      <CardHeader className="pb-3 border-b border-slate-100">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <CardTitle className="text-base font-bold text-slate-900 flex items-center gap-2">
              <span>Strategy Evaluation: Naive Baseline vs. AI Multi-Agent</span>
              <Badge variant="outline" className="bg-emerald-50 text-emerald-700 border-emerald-200 font-semibold text-[11px]">
                Measured Money Recovered
              </Badge>
            </CardTitle>
            <CardDescription className="text-xs">
              Direct mathematical comparison across identical failure cohorts with policy compliance
            </CardDescription>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-500">Net Additional Won:</span>
            <span className="font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
              +{formatCurrency(upliftInr)} (+{formatPercent(upliftPercent)})
            </span>
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-0">
        <div className="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-slate-100">
          {/* Baseline Column */}
          <div className="p-4 sm:p-5 space-y-3 bg-slate-50/50">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">Naive Baseline</span>
              <Badge variant="secondary" className="text-[10px]">Retry-Once Only</Badge>
            </div>
            <div className="space-y-1">
              <div className="text-2xl font-bold text-slate-800">
                {formatCurrency(baseRecovered)}
              </div>
              <div className="text-xs text-slate-500">
                Recovery Rate: <span className="font-semibold text-slate-700">{formatPercent(baseRate)}</span>
              </div>
            </div>
            <div className="text-[11px] text-slate-500 space-y-1 pt-1 border-t border-slate-200/60">
              <div>• Blind 24h retry with zero context</div>
              <div>• No RAG precedents or customer telemetry</div>
              <div>• Fixed 50 paise communication cost per attempt</div>
            </div>
          </div>

          {/* AI Orchestrator Column */}
          <div className="p-4 sm:p-5 space-y-3 bg-blue-50/30">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-blue-900 uppercase tracking-wider flex items-center gap-1">
                <Zap className="w-3.5 h-3.5 text-blue-600" />
                AI Multi-Agent
              </span>
              <Badge variant="default" className="bg-brand-600 text-white text-[10px]">RAG + Policy Gate</Badge>
            </div>
            <div className="space-y-1">
              <div className="text-2xl font-bold text-blue-700">
                {formatCurrency(aiRecovered)}
              </div>
              <div className="text-xs text-blue-800">
                Recovery Rate: <span className="font-bold text-blue-900">{formatPercent(aiRate)}</span>
              </div>
            </div>
            <div className="text-[11px] text-slate-600 space-y-1 pt-1 border-t border-blue-200/50">
              <div>• 7-agent specialized LangGraph orchestration</div>
              <div>• Empirical confidence from ChromaDB playbook</div>
              <div>• Multi-channel dispatch (Hinglish/Email/WhatsApp)</div>
            </div>
          </div>

          {/* Verified Uplift Column */}
          <div className="p-4 sm:p-5 space-y-3 bg-emerald-50/40">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-emerald-900 uppercase tracking-wider flex items-center gap-1">
                <ArrowUpRight className="w-3.5 h-3.5 text-emerald-600" />
                Net Value Delivered
              </span>
              <Badge variant="outline" className="bg-emerald-100 text-emerald-800 border-emerald-300 text-[10px] font-bold">
                +{formatPercent(upliftPercent)}
              </Badge>
            </div>
            <div className="space-y-1">
              <div className="text-2xl font-bold text-emerald-700">
                +{formatCurrency(upliftInr)}
              </div>
              <div className="text-xs text-emerald-800">
                Net ROI: <span className="font-bold text-emerald-900">{formatPercent(metrics.net_roi_percent || 0)}</span>
              </div>
            </div>
            <div className="text-[11px] text-slate-600 space-y-1 pt-1 border-t border-emerald-200/60">
              <div>• {metrics.policy_interventions_count} policy stopping rules enforced</div>
              <div>• 100% deterministic audit trail recorded</div>
              <div>• ₹{atRisk.toLocaleString('en-IN', { maximumFractionDigits: 0 })} total failure cohort value analyzed</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
