import React from 'react';
import { Activity, ChevronRight, CheckCircle, AlertTriangle, ShieldAlert, XCircle, Clock, Database } from 'lucide-react';
import type { RecoveryCaseResponse } from '../../../types/recovery';
import { SEGMENT_BADGES } from '../../../constants/segmentBadges';

export interface CasesTableProps {
  cases: RecoveryCaseResponse[];
  isLoading: boolean;
  onSelectCase: (caseId: string) => void;
}

export const CasesTable: React.FC<CasesTableProps> = ({
  cases,
  isLoading,
  onSelectCase,
}) => {
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'RECOVERED':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle className="w-3 h-3 mr-1" /> Recovered
          </span>
        );
      case 'ESCALATED':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <AlertTriangle className="w-3 h-3 mr-1" /> Escalated
          </span>
        );
      case 'BLOCKED':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <ShieldAlert className="w-3 h-3 mr-1" /> Blocked by Policy
          </span>
        );
      case 'FAILED':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-700 text-slate-300 border border-slate-600">
            <XCircle className="w-3 h-3 mr-1" /> Failed
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <Clock className="w-3 h-3 mr-1" /> In Progress
          </span>
        );
    }
  };

  const getPrecedentBadge = (hasSufficient?: boolean, count?: number) => {
    if (hasSufficient === false) {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-semibold bg-amber-500/10 text-amber-300 border border-amber-500/30">
          <AlertTriangle className="w-3 h-3 mr-1 text-amber-400" />
          Insufficient (n={count || 0})
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-500/30">
        <Database className="w-3 h-3 mr-1 text-emerald-400" />
        Sufficient (n={count || 3})
      </span>
    );
  };

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

  const getSegmentBadge = (segment: string) => {
    const config = SEGMENT_BADGES[segment as keyof typeof SEGMENT_BADGES] || {
      label: segment.replace('_', ' '),
      bg: 'bg-slate-800',
      text: 'text-slate-300',
      border: 'border-slate-700',
    };
    return (
      <span
        className={`px-2 py-0.5 rounded text-[11px] font-mono border ${config.bg} ${config.text} ${config.border}`}
      >
        {config.label}
      </span>
    );
  };

  return (
    <div className="overflow-hidden rounded-2xl bg-[#0c2340]/80 border border-slate-800 shadow-2xl">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
            <tr>
              <th className="px-5 py-4">Case ID</th>
              <th className="px-5 py-4">Customer</th>
              <th className="px-5 py-4">Segment</th>
              <th className="px-5 py-4">At Risk</th>
              <th className="px-5 py-4">Precedent</th>
              <th className="px-5 py-4">Status</th>
              <th className="px-5 py-4">Promise-to-Pay</th>
              <th className="px-5 py-4">Recovered ₹</th>
              <th className="px-5 py-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {isLoading ? (
              <tr>
                <td colSpan={9} className="px-5 py-12 text-center text-slate-500">
                  <Activity className="w-6 h-6 animate-spin mx-auto mb-2 text-brand-400" />
                  Loading cases from database...
                </td>
              </tr>
            ) : cases.length === 0 ? (
              <tr>
                <td colSpan={9} className="px-5 py-12 text-center text-slate-500">
                  No recovery cases found matching your filters.
                </td>
              </tr>
            ) : (
              cases.map((c) => (
                <tr
                  key={c.id}
                  onClick={() => onSelectCase(c.id)}
                  className="hover:bg-slate-800/40 cursor-pointer transition"
                >
                  <td className="px-5 py-4 font-mono font-bold text-brand-300">
                    {c.id.substring(0, 12)}
                  </td>
                  <td className="px-5 py-4">
                    <div className="font-semibold text-white">{c.customer_name}</div>
                    <div className="text-[11px] text-slate-400">{c.customer_email}</div>
                  </td>
                  <td className="px-5 py-4">{getSegmentBadge(c.customer_segment)}</td>
                  <td className="px-5 py-4 font-semibold text-white">
                    ₹{c.leak_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </td>
                  <td className="px-5 py-4">
                    {getPrecedentBadge(c.has_sufficient_precedent, c.precedent_count)}
                  </td>
                  <td className="px-5 py-4">{getStatusBadge(c.status)}</td>
                  <td className="px-5 py-4">{getPromiseBadge(c.promise_status)}</td>
                  <td className="px-5 py-4 font-bold text-emerald-400">
                    {c.recovered_amount > 0
                      ? `₹${c.recovered_amount.toLocaleString('en-IN', {
                          minimumFractionDigits: 2,
                        })}`
                      : '—'}
                  </td>
                  <td className="px-5 py-4 text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectCase(c.id);
                      }}
                      className="p-1.5 rounded-lg bg-slate-800 hover:bg-brand-600 text-slate-300 hover:text-white transition"
                    >
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
