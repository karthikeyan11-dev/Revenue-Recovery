import React from 'react';
import { X, Activity, User, Database, AlertTriangle, CheckCircle, ShieldAlert, XCircle, Clock } from 'lucide-react';
import { useRecoveryCaseDetail } from '../hooks/useRecoveryCaseDetail';
import { PromiseCard } from './PromiseCard';
import { ActionsList } from './ActionsList';
import { TimelineView } from './TimelineView';
import { SEGMENT_BADGES } from '../../../constants/segmentBadges';

export interface CaseDetailDrawerProps {
  caseId: string | null;
  onClose: () => void;
}

export const CaseDetailDrawer: React.FC<CaseDetailDrawerProps> = ({ caseId, onClose }) => {
  const { data: caseDetail, isLoading: isLoadingDetail } = useRecoveryCaseDetail(caseId || '');

  if (!caseId) return null;

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
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex justify-end animate-in slide-in-from-right duration-200">
      <div className="w-full max-w-2xl bg-[#09182d] border-l border-slate-800 h-full overflow-y-auto shadow-2xl flex flex-col">
        {/* Drawer Header */}
        <div className="p-6 border-b border-slate-800 flex items-center justify-between sticky top-0 bg-[#09182d] z-10">
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-mono text-sm font-bold text-brand-400">
                {caseId}
              </span>
              {caseDetail && getStatusBadge(caseDetail.status)}
            </div>
            <h3 className="text-lg font-bold text-white mt-1">
              Recovery Case & Decision Audit
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Drawer Body */}
        <div className="p-6 space-y-6 flex-1">
          {isLoadingDetail || !caseDetail ? (
            <div className="py-16 text-center text-slate-500">
              <Activity className="w-8 h-8 animate-spin mx-auto mb-2 text-brand-400" />
              Loading case intelligence...
            </div>
          ) : (
            <>
              {/* Customer 360 Card */}
              <div className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div className="flex items-center space-x-2 text-brand-400 font-bold text-xs uppercase tracking-wider">
                    <User className="w-4 h-4" />
                    <span>Customer Profile & Risk Telemetry</span>
                  </div>
                  {getSegmentBadge(caseDetail.customer_segment)}
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
                  <div>
                    <span className="text-slate-500 block">Name</span>
                    <span className="font-semibold text-white">{caseDetail.customer_name}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">At-Risk Amount</span>
                    <span className="font-bold text-white">
                      ₹{caseDetail.leak_amount.toLocaleString('en-IN')}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Precedent Grounding</span>
                    <div className="mt-0.5">
                      {getPrecedentBadge(
                        caseDetail.has_sufficient_precedent,
                        caseDetail.precedent_count
                      )}
                    </div>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Recovered Amount</span>
                    <span className="font-bold text-emerald-400">
                      ₹{caseDetail.recovered_amount.toLocaleString('en-IN')}
                    </span>
                  </div>
                </div>
              </div>

              {/* Promise-to-Pay Tracker Section */}
              <PromiseCard promises={caseDetail.promises} />

              {/* Actions & Policy Decision Box */}
              <ActionsList actions={caseDetail.actions} />

              {/* Vertical Audit Timeline */}
              <TimelineView timeline={caseDetail.timeline} />
            </>
          )}
        </div>
      </div>
    </div>
  );
};
