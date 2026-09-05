import React from 'react';
import type { StrategyMetricsResponse } from '../../../types/metrics';

export interface MetricCardProps {
  title: string;
  metrics?: StrategyMetricsResponse | null;
  accentColor?: string;
  badge?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  metrics,
  accentColor = 'border-slate-700',
  badge,
}) => {
  if (!metrics) {
    return (
      <div className={`bg-[#0c2340]/40 border ${accentColor} rounded-xl p-5 backdrop-blur-sm`}>
        <h4 className="text-sm font-semibold text-slate-300">{title}</h4>
        <p className="text-xs text-slate-500 mt-4 italic">No simulation runs executed yet.</p>
      </div>
    );
  }

  return (
    <div className={`bg-[#0c2340]/60 border ${accentColor} rounded-xl p-5 backdrop-blur-sm shadow-lg`}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <h4 className="text-sm font-semibold text-white tracking-tight">{title}</h4>
        {badge && (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-medium bg-slate-800 text-slate-300 border border-slate-700">
            {badge}
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4 mt-4 text-xs">
        <div>
          <div className="text-slate-400">Recovery Rate</div>
          <div className="text-lg font-bold text-white mt-0.5">
            {metrics.recovery_rate_percent.toFixed(1)}%
          </div>
        </div>
        <div>
          <div className="text-slate-400">Recovered Revenue</div>
          <div className="text-lg font-bold text-emerald-400 mt-0.5">
            ₹{metrics.total_recovered_revenue.toLocaleString('en-IN')}
          </div>
        </div>
        <div>
          <div className="text-slate-400">Total Revenue At Risk</div>
          <div className="text-sm font-semibold text-slate-300 mt-0.5">
            ₹{metrics.total_revenue_at_risk.toLocaleString('en-IN')}
          </div>
        </div>
        <div>
          <div className="text-slate-400">Execution Cost</div>
          <div className="text-sm font-semibold text-rose-300 mt-0.5">
            ₹{(metrics.total_cost || 0).toLocaleString('en-IN')}
          </div>
        </div>
        <div>
          <div className="text-slate-400">Cases Processed</div>
          <div className="text-sm font-semibold text-slate-300 mt-0.5">
            {metrics.cases_count} cases
          </div>
        </div>
        <div>
          <div className="text-slate-400">Net ROI</div>
          <div className="text-sm font-semibold text-brand-300 mt-0.5">
            {metrics.net_roi_percent.toFixed(1)}%
          </div>
        </div>
      </div>
    </div>
  );
};
