import React from 'react';
import { Sparkles, TrendingUp } from 'lucide-react';
import type { StrategyComparisonResponse } from '../../../types/metrics';

export interface ROIHeroProps {
  comparison?: StrategyComparisonResponse | null;
}

export const ROIHero: React.FC<ROIHeroProps> = ({ comparison }) => {
  if (!comparison) return null;

  const aiCost = comparison.ai_metrics?.total_cost || 0;
  const netAdvantage = comparison.uplift_inr - aiCost;

  return (
    <div className="bg-gradient-to-r from-brand-950/60 via-[#0c2340] to-emerald-950/60 border border-brand-500/30 rounded-2xl p-6 shadow-xl relative overflow-hidden backdrop-blur-sm">
      <div className="absolute top-0 right-0 p-6 opacity-10 pointer-events-none">
        <Sparkles className="h-36 w-36 text-brand-400" />
      </div>

      <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              Autonomous AI Uplift Verified
            </span>
            <span className="text-xs text-slate-400 font-mono">
              vs Naive Baseline Retry
            </span>
          </div>

          <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-2">
            +₹{comparison.uplift_inr.toLocaleString('en-IN')}{' '}
            <span className="text-emerald-400 text-xl font-bold">
              (+{comparison.uplift_percent.toFixed(1)}% Recovered)
            </span>
          </h2>
          <p className="text-xs sm:text-sm text-slate-300 mt-1 max-w-2xl">
            Multi-agent contextual dispatch (Smart UPI Retries + WhatsApp Promises + Frictionless Discounts) vastly outperforms naive single-retry scripts.
          </p>
        </div>

        <div className="flex items-center gap-4 bg-[#07162c]/80 border border-slate-700/60 rounded-xl p-4">
          <div>
            <div className="text-[11px] text-slate-400 uppercase font-medium">
              Net AI Advantage
            </div>
            <div className="text-xl font-black text-brand-300 mt-0.5">
              +₹{netAdvantage.toLocaleString('en-IN')}
            </div>
            <div className="text-[10px] text-slate-400 mt-0.5">
              After ₹{aiCost.toLocaleString('en-IN')} execution costs
            </div>
          </div>
        </div>
      </div>

      {comparison.key_findings && comparison.key_findings.length > 0 && (
        <div className="mt-5 pt-4 border-t border-slate-800/80 grid grid-cols-1 md:grid-cols-3 gap-3">
          {comparison.key_findings.map((finding: string, idx: number) => (
            <div key={idx} className="flex items-start space-x-2 text-xs text-slate-300 bg-slate-900/40 p-2.5 rounded-lg border border-slate-800/50">
              <TrendingUp className="h-4 w-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>{finding}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
