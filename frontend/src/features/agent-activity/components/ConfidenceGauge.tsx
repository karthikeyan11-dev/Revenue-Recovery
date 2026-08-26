import React from 'react';
import { Database, AlertTriangle, Sparkles } from 'lucide-react';

export interface ConfidenceGaugeProps {
  confidence?: number | null;
  llmStatedConfidence?: number | null;
  sampleSize?: number | null;
}

export const ConfidenceGauge: React.FC<ConfidenceGaugeProps> = ({
  confidence,
  llmStatedConfidence,
  sampleSize,
}) => {
  if (confidence === null || confidence === undefined) return null;

  const pct = Math.round(confidence * 100);
  const isColdStart = (sampleSize ?? 0) < 5;

  return (
    <div className="flex flex-wrap items-center gap-3 p-3 rounded-lg bg-slate-900/90 border border-slate-800 text-xs">
      <div className="flex items-center space-x-2">
        <div className="h-6 w-6 rounded-full bg-brand-500/20 text-brand-300 flex items-center justify-center font-bold text-[11px] border border-brand-500/30">
          {pct}%
        </div>
        <div>
          <span className="font-semibold text-white">Laplace Empirical Confidence</span>
          <span className="text-[10px] text-slate-400 block font-mono">
            {isColdStart ? (
              <span className="text-amber-400 flex items-center gap-1">
                <AlertTriangle className="h-3 w-3 inline" />
                Cold Start Prior (n={sampleSize || 0})
              </span>
            ) : (
              <span className="text-emerald-400 flex items-center gap-1">
                <Database className="h-3 w-3 inline" />
                Historical Evidence Grounded (n={sampleSize})
              </span>
            )}
          </span>
        </div>
      </div>

      {llmStatedConfidence !== null && llmStatedConfidence !== undefined && (
        <div className="ml-auto flex items-center space-x-1 text-[11px] text-slate-400 border-l border-slate-800 pl-3">
          <Sparkles className="h-3 w-3 text-amber-300" />
          <span>LLM Stated: {Math.round(llmStatedConfidence * 100)}%</span>
        </div>
      )}
    </div>
  );
};
