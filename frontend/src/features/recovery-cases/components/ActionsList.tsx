import React from 'react';
import { ShieldAlert } from 'lucide-react';

export interface ActionItem {
  id?: string;
  proposed_action?: string | null;
  policy_decision?: string | null;
  policy_reasoning?: string | null;
}

export interface ActionsListProps {
  actions?: ActionItem[] | null;
}

export const ActionsList: React.FC<ActionsListProps> = ({ actions }) => {
  if (!actions || actions.length === 0) return null;

  return (
    <div className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-3">
      <div className="flex items-center space-x-2 text-indigo-400 font-bold text-xs uppercase tracking-wider">
        <ShieldAlert className="w-4 h-4" />
        <span>Deterministic Policy Engine Intervention</span>
      </div>
      {actions.map((act, i) => (
        <div
          key={act.id || i}
          className="p-3 rounded-lg bg-slate-800/60 border border-slate-700/60 space-y-2"
        >
          <div className="flex items-center justify-between">
            <span className="font-semibold text-white text-xs">
              Action: {act.proposed_action || 'UNKNOWN'}
            </span>
            <span
              className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                act.policy_decision === 'APPROVED'
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : act.policy_decision === 'REJECTED'
                  ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                  : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
              }`}
            >
              Policy: {act.policy_decision || 'PENDING'}
            </span>
          </div>
          {act.policy_reasoning && (
            <p className="text-xs text-slate-300">{act.policy_reasoning}</p>
          )}
        </div>
      ))}
    </div>
  );
};
