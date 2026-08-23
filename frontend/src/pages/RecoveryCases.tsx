import React, { useState } from 'react';
import {
  Search,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  ShieldAlert,
  ChevronRight,
  X,
  User,
  Zap,
  Activity,
  Database,
  Calendar,
  Layers,
} from 'lucide-react';
import { useCasesQuery, useCaseDetailQuery } from '../api/hooks/useCases';
import type { CaseStatus } from '../api/generated';

export const RecoveryCases: React.FC = () => {
  const [selectedStatus, setSelectedStatus] = useState<CaseStatus | 'ALL'>('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);

  const { data: casesData, isLoading } = useCasesQuery({
    status: selectedStatus === 'ALL' ? undefined : (selectedStatus as CaseStatus),
    limit: 100,
  });

  const { data: caseDetail, isLoading: isLoadingDetail } = useCaseDetailQuery(selectedCaseId || '');

  const filteredItems = (casesData?.items || []).filter((item) => {
    if (!searchTerm.trim()) return true;
    const term = searchTerm.toLowerCase();
    return (
      item.id.toLowerCase().includes(term) ||
      item.customer_name.toLowerCase().includes(term) ||
      item.customer_email.toLowerCase().includes(term) ||
      item.customer_segment.toLowerCase().includes(term)
    );
  });

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
    if (!status) {
      return <span className="text-slate-600 font-mono text-[11px]">—</span>;
    }
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
    const colors: Record<string, string> = {
      HIGH_VALUE: 'bg-purple-500/10 text-purple-300 border-purple-500/30',
      LOYAL: 'bg-indigo-500/10 text-indigo-300 border-indigo-500/30',
      REGULAR: 'bg-slate-700/50 text-slate-300 border-slate-600',
      AT_RISK: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
      CHURNING: 'bg-rose-500/10 text-rose-300 border-rose-500/30',
      LOW_VALUE: 'bg-slate-800 text-slate-400 border-slate-700',
    };
    return (
      <span
        className={`px-2 py-0.5 rounded text-[11px] font-mono border ${
          colors[segment] || 'bg-slate-800 text-slate-300 border-slate-700'
        }`}
      >
        {segment.replace('_', ' ')}
      </span>
    );
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-[#0c2340]/90 border border-slate-800 backdrop-blur shadow-xl">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Recovery Cases Management</h2>
          <p className="text-xs text-slate-400 mt-1">
            Browse payment failure events, examine empirical precedent grounds, inspect policy
            gates, and monitor promises-to-pay.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Search bar */}
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search customer, email, case..."
              className="pl-9 pr-4 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500 w-64"
            />
          </div>

          {/* Status Filter buttons */}
          <div className="flex items-center space-x-1 p-1 rounded-xl bg-slate-900 border border-slate-800">
            {(['ALL', 'RECOVERED', 'IN_PROGRESS', 'ESCALATED', 'BLOCKED', 'FAILED'] as const).map(
              (status) => (
                <button
                  key={status}
                  onClick={() => setSelectedStatus(status)}
                  className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition ${
                    selectedStatus === status
                      ? 'bg-brand-600 text-white font-semibold'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {status === 'ALL' ? 'All' : status.replace('_', ' ')}
                </button>
              )
            )}
          </div>
        </div>
      </div>

      {/* Cases Table */}
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
              ) : filteredItems.length === 0 ? (
                <tr>
                  <td colSpan={9} className="px-5 py-12 text-center text-slate-500">
                    No recovery cases found matching your filters.
                  </td>
                </tr>
              ) : (
                filteredItems.map((c) => (
                  <tr
                    key={c.id}
                    onClick={() => setSelectedCaseId(c.id)}
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
                          setSelectedCaseId(c.id);
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

      {/* Case Detail Slide-over Modal */}
      {selectedCaseId && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex justify-end animate-fadeIn">
          <div className="w-full max-w-2xl bg-[#09182d] border-l border-slate-800 h-full overflow-y-auto shadow-2xl flex flex-col">
            {/* Drawer Header */}
            <div className="p-6 border-b border-slate-800 flex items-center justify-between sticky top-0 bg-[#09182d] z-10">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-mono text-sm font-bold text-brand-400">
                    {selectedCaseId}
                  </span>
                  {caseDetail && getStatusBadge(caseDetail.status)}
                </div>
                <h3 className="text-lg font-bold text-white mt-1">
                  Recovery Case & Decision Audit
                </h3>
              </div>
              <button
                onClick={() => setSelectedCaseId(null)}
                className="p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-white"
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
                  <div className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-3">
                    <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                      <div className="flex items-center space-x-2 text-cyan-400 font-bold text-xs uppercase tracking-wider">
                        <Calendar className="w-4 h-4" />
                        <span>Promise-to-Pay Commitment Tracking</span>
                      </div>
                      {caseDetail.promises && caseDetail.promises.length > 0 && (
                        <span className="text-[11px] font-mono text-slate-400">
                          {caseDetail.promises.length} Commitment(s)
                        </span>
                      )}
                    </div>

                    {caseDetail.promises && caseDetail.promises.length > 0 ? (
                      <div className="space-y-3">
                        {caseDetail.promises.map((p) => (
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
                                ⚠️ Promise broken after follow-up. Stopping rule triggered: Case
                                escalated to human agent.
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="p-3 rounded-lg bg-slate-800/40 border border-slate-800 text-xs text-slate-400 flex items-center space-x-2">
                        <Layers className="w-4 h-4 text-slate-500" />
                        <span>
                          No active payment commitment required for this case (direct gateway retry
                          or non-interactive outreach).
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Actions & Policy Decision Box */}
                  {caseDetail.actions && caseDetail.actions.length > 0 && (
                    <div className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-3">
                      <div className="flex items-center space-x-2 text-indigo-400 font-bold text-xs uppercase tracking-wider">
                        <ShieldAlert className="w-4 h-4" />
                        <span>Deterministic Policy Engine Intervention</span>
                      </div>
                      {caseDetail.actions.map((act) => (
                        <div
                          key={act.id}
                          className="p-3 rounded-lg bg-slate-800/60 border border-slate-700/60 space-y-2"
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-semibold text-white text-xs">
                              Action: {act.proposed_action}
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
                              Policy: {act.policy_decision}
                            </span>
                          </div>
                          <p className="text-xs text-slate-300">{act.policy_reasoning}</p>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Vertical Audit Timeline */}
                  <div className="space-y-4">
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center space-x-2">
                      <Zap className="w-4 h-4 text-brand-400" />
                      <span>Multi-Agent Workflow Audit Trail</span>
                    </h4>

                    <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
                      {(caseDetail.timeline || []).map((item) => (
                        <div key={item.id} className="relative space-y-1">
                          {/* Dot */}
                          <div className="absolute -left-6 top-1 w-2.5 h-2.5 rounded-full bg-brand-500 border-2 border-[#09182d]" />

                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold text-white">{item.agent}</span>
                            <span className="text-[11px] font-mono text-slate-500">
                              {new Date(item.timestamp).toLocaleTimeString()}
                            </span>
                          </div>

                          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs space-y-1.5">
                            <div className="flex items-center justify-between text-slate-400">
                              <span className="font-mono text-[11px] text-brand-300">
                                {item.step_name}
                              </span>
                              <span className="text-emerald-400 font-semibold">
                                {item.decision}
                              </span>
                            </div>
                            <p className="text-slate-300">{item.output_summary}</p>
                            <p className="text-[11px] text-slate-500 italic">
                              Input: {item.input_summary}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
