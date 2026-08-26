import React from 'react';
import { Calendar, CheckCircle, XCircle, Clock, Layers } from 'lucide-react';
import type { PromiseToPayResponse } from '../../../types/recovery';

export interface PromiseCardProps {
  promises?: PromiseToPayResponse[] | null;
}

export const PromiseCard: React.FC<PromiseCardProps> = ({ promises }) => {
  const getPromiseBadge = (status?: string | null) => {
    if (!status) return <span className="text-slate-600 font-mono text-[11px]">—</span>;
    switch (status) {
      case 'KEPT':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle className="w-3 h-3 mr-1" /> Kept
          </span>
        );
      case 'BROKEN':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <XCircle className="w-3 h-3 mr-1" /> Broken
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Clock className="w-3 h-3 mr-1" /> Pending
          </span>
        );
    }
  };

  return (
    <div className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-3">
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <div className="flex items-center space-x-2 text-cyan-400 font-bold text-xs uppercase tracking-wider">
          <Calendar className="w-4 h-4" />
          <span>Promise-to-Pay Commitment Tracking</span>
        </div>
        {promises && promises.length > 0 && (
          <span className="text-[11px] font-mono text-slate-400">
            {promises.length} Commitment(s)
          </span>
        )}
      </div>

      {promises && promises.length > 0 ? (
        <div className="space-y-3">
          {promises.map((p) => (
            <div
              key={p.id}
              className="p-3.5 rounded-lg bg-slate-800/70 border border-slate-700/70 space-y-2"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-cyan-300">
                  {p.id}
                </span>
                {getPromiseBadge(p.status)}
              </div>
              <div className="grid grid-cols-3 gap-2 text-xs pt-1">
                <div>
                  <span className="text-slate-500 block text-[11px]">
                    Committed Amount
                  </span>
                  <span className="font-bold text-white">
                    ₹{p.committed_amount.toLocaleString('en-IN')}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[11px]">Due Target</span>
                  <span className="font-medium text-slate-300">
                    {new Date(p.committed_date).toLocaleDateString()}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[11px]">
                    Follow-up Count
                  </span>
                  <span className="font-mono font-medium text-amber-300">
                    {p.follow_up_count} / 1 (max retry)
                  </span>
                </div>
              </div>
              {p.status === 'BROKEN' && (p.follow_up_count ?? 0) >= 1 && (
                <div className="p-2 rounded bg-rose-500/10 border border-rose-500/20 text-[11px] text-rose-300">
                  ⚠️ Promise broken after follow-up. Stopping rule triggered: Case escalated to human agent.
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="p-3 rounded-lg bg-slate-800/40 border border-slate-800 text-xs text-slate-400 flex items-center space-x-2">
          <Layers className="w-4 h-4 text-slate-500" />
          <span>
            No active payment commitment required for this case (direct gateway retry or non-interactive outreach).
          </span>
        </div>
      )}
    </div>
  );
};
