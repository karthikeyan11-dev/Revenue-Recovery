import React from 'react';
import { Database, Sparkles, CheckCircle2, XCircle } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '../../../components/ui/dialog';
import { Badge } from '../../../components/ui/badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../../../components/ui/tabs';
import { formatCurrency, formatDate, formatPercent } from '../../../lib/utils';
import { RECOVERY_CASES_CONSTANTS } from '../constants/recovery-cases.constants';
import type { RecoveryCaseDetailDrawerProps } from '../types/recovery-cases.types';

const CANONICAL_STEP_ORDER: Record<string, number> = {
  LEAK_DETECTION: 1,
  PROFILE_ANALYSIS: 2,
  STRATEGY_PROPOSAL: 3,
  POLICY_GATE: 4,
  DISPATCH_OUTCOME: 5,
  PLAYBOOK_LEARNING_WRITEBACK: 6,
};

export const RecoveryCaseDetailDrawer: React.FC<RecoveryCaseDetailDrawerProps> = ({
  caseDetail,
  isOpen,
  onClose,
}) => {
  if (!caseDetail) return null;

  const sortedTimeline = [...caseDetail.timeline].sort(
    (a, b) =>
      (CANONICAL_STEP_ORDER[a.step_name] ?? 99) - (CANONICAL_STEP_ORDER[b.step_name] ?? 99)
  );

  const formatSummary = (text: string) => {
    return text.replace(/\((\d+)\/(\d+)\s+attempts\)/g, '($1 successful / $2 lifetime transactions)');
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-3xl max-h-[85vh] overflow-y-auto p-6">
        <DialogHeader className="border-b border-slate-100 pb-4">
          <div className="flex items-center justify-between pr-6">
            <div>
              <DialogTitle className="text-lg font-bold text-slate-900">
                {caseDetail.id}
              </DialogTitle>
              <DialogDescription className="text-xs text-slate-500 mt-0.5">
                {RECOVERY_CASES_CONSTANTS.DRAWER.SUBTITLE}
              </DialogDescription>
            </div>
            <Badge
              variant={
                caseDetail.status === 'RECOVERED'
                  ? 'success'
                  : caseDetail.status === 'ESCALATED'
                  ? 'warning'
                  : 'destructive'
              }
              className="text-xs px-2.5 py-0.5 uppercase tracking-wide"
            >
              {caseDetail.status}
            </Badge>
          </div>
        </DialogHeader>

        {/* Overview Stats Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 my-4">
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200/70">
            <div className="text-[11px] font-semibold text-slate-500 uppercase">Customer</div>
            <div className="text-xs font-bold text-slate-900 mt-1 truncate">
              {caseDetail.customer_name}
            </div>
            <div className="text-[11px] text-slate-400 truncate">{caseDetail.customer_email}</div>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200/70">
            <div className="text-[11px] font-semibold text-slate-500 uppercase">Leak Amount</div>
            <div className="text-xs font-bold text-slate-900 mt-1">
              {formatCurrency(caseDetail.leak_amount ?? 0)}
            </div>
            <div className="text-[11px] text-emerald-600 font-medium">
              Recovered: {formatCurrency(caseDetail.recovered_amount || 0)}
            </div>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200/70">
            <div className="text-[11px] font-semibold text-slate-500 uppercase">Case Status</div>
            <div className="text-xs font-bold text-slate-900 mt-1">{caseDetail.status}</div>
            <Badge variant="destructive" className="mt-1 text-[10px] px-1.5 py-0">
              {caseDetail.priority} PRIORITY
            </Badge>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200/70">
            <div className="text-[11px] font-semibold text-slate-500 uppercase">Failure Reason</div>
            <div className="text-xs font-bold text-slate-900 mt-1 truncate">
              {caseDetail.failure_reason}
            </div>
            <div className="text-[11px] text-slate-400 font-mono">{caseDetail.failure_code}</div>
          </div>
        </div>

        {/* Tabbed Detailed View */}
        <Tabs defaultValue="timeline" className="w-full">
          <TabsList className="grid grid-cols-3 w-full sm:w-[460px] mb-4">
            <TabsTrigger value="timeline">
              {RECOVERY_CASES_CONSTANTS.DRAWER.TIMELINE_TAB}
            </TabsTrigger>
            <TabsTrigger value="actions">
              {RECOVERY_CASES_CONSTANTS.DRAWER.ACTIONS_TAB}
            </TabsTrigger>
            <TabsTrigger value="precedents" className="flex items-center space-x-1">
              <Database className="w-3 h-3 mr-1 text-blue-500" />
              <span>{RECOVERY_CASES_CONSTANTS.DRAWER.PRECEDENTS_TAB}</span>
            </TabsTrigger>
          </TabsList>

          {/* Timeline Tab */}
          <TabsContent value="timeline" className="space-y-4">
            {caseDetail.timeline.length === 0 ? (
              <div className="text-center py-6 text-xs text-slate-500">
                No timeline events recorded for this case.
              </div>
            ) : (
              <div className="space-y-3 relative before:absolute before:inset-0 before:left-3.5 before:w-0.5 before:bg-slate-200">
                {sortedTimeline.map((step, idx) => (
                  <div key={idx} className="relative flex items-start space-x-4 pl-8">
                    <div className="absolute left-2 top-1.5 w-3.5 h-3.5 rounded-full bg-blue-600 ring-4 ring-white" />
                    <div className="flex-1 bg-slate-50/80 p-3.5 rounded-lg border border-slate-200/60 space-y-1.5">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <span className="text-xs font-bold text-slate-900">{step.agent}</span>
                          <span className="text-[11px] font-mono text-slate-400 bg-white px-1.5 py-0.5 rounded border border-slate-200">
                            {step.step_name}
                          </span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-[11px] text-slate-500">
                            Confidence: {formatPercent(step.confidence * 100)}
                          </span>
                          <span className="text-[11px] text-slate-400">
                            {formatDate(step.timestamp)}
                          </span>
                        </div>
                      </div>
                      <div className="text-xs text-slate-700">
                        <span className="font-semibold text-slate-900">Decision: </span>
                        {step.decision}
                      </div>
                      {step.output_summary && (
                        <div className="text-[11px] text-slate-600 bg-white p-2 rounded border border-slate-100 font-mono leading-relaxed">
                          {formatSummary(step.output_summary)}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </TabsContent>

          {/* Actions Tab */}
          <TabsContent value="actions" className="space-y-3">
            {caseDetail.actions.length === 0 ? (
              <div className="text-center py-6 text-xs text-slate-500">
                No recovery actions recorded for this case.
              </div>
            ) : (
              <div className="space-y-2">
                {caseDetail.actions.map((act) => (
                  <div
                    key={act.id}
                    className="p-3 bg-slate-50 rounded-lg border border-slate-200/70 flex items-center justify-between"
                  >
                    <div>
                      <div className="text-xs font-bold text-slate-900">{act.action_type}</div>
                      <div className="text-[11px] text-slate-500">
                        Policy Decision: <span className="font-semibold text-slate-700">{act.policy_decision}</span> • Cost: {formatCurrency(act.cost)}
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge
                        variant={act.success ? 'success' : 'secondary'}
                        className="text-[11px]"
                      >
                        {act.status}
                      </Badge>
                      <div className="text-[10px] text-slate-400 mt-0.5">
                        {formatDate(act.executed_at)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </TabsContent>

          {/* RAG Precedents Tab (ChromaDB Real-Time Query Results) */}
          <TabsContent value="precedents" className="space-y-4">
            <div className="bg-gradient-to-r from-blue-50/80 to-indigo-50/80 border border-blue-200/70 rounded-xl p-3.5 flex items-start space-x-3">
              <Database className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
              <div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-bold text-blue-900">
                    ChromaDB Vector Store Precedents (k=5 Grounded Matches)
                  </span>
                  <Badge variant="outline" className="text-[10px] bg-blue-100/60 text-blue-700 border-blue-200">
                    Live Vector Retrieval
                  </Badge>
                </div>
                <p className="text-[11px] text-blue-700/90 mt-1 leading-relaxed">
                  The Recovery Strategist dynamically queried collection <code className="font-mono bg-blue-100 px-1 py-0.5 rounded text-blue-800">recovery_playbook</code> for historical cases matching failure reason <strong>{caseDetail.failure_reason}</strong>. These empirical outcomes directly grounded the agent's confidence score and proposed action.
                </p>
              </div>
            </div>

            {(!caseDetail.retrieved_precedents || caseDetail.retrieved_precedents.length === 0) ? (
              <div className="text-center py-8 text-xs text-slate-500 bg-slate-50 rounded-xl border border-slate-200">
                <Sparkles className="w-6 h-6 text-slate-400 mx-auto mb-2" />
                No historical precedents retrieved from ChromaDB for this failure profile.
              </div>
            ) : (
              <div className="space-y-2.5">
                {caseDetail.retrieved_precedents.map((p, pIdx) => {
                  const isSuccess = p.is_recovered || p.outcome === 'RECOVERED' || p.outcome === 'SUCCESS';
                  return (
                    <div
                      key={pIdx}
                      className="p-3 bg-white rounded-xl border border-slate-200/80 shadow-sm hover:border-slate-300 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center space-x-2">
                          <span className="font-mono text-xs font-bold text-slate-800">
                            {p.case_id}
                          </span>
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-semibold uppercase">
                            {p.failure_reason}
                          </span>
                          {p.segment && (
                            <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200">
                              {p.segment}
                            </span>
                          )}
                        </div>
                        <div className="text-xs text-slate-600 flex items-center space-x-2">
                          <span>Action: <strong className="text-slate-800">{p.action_taken}</strong></span>
                          <span>•</span>
                          <span>Channel: <strong className="text-slate-800">{p.channel || 'DIRECT'}</strong></span>
                        </div>
                      </div>

                      <div className="flex items-center space-x-3 self-end sm:self-center">
                        <div className="text-right">
                          <div className="text-xs font-bold text-slate-900">
                            {formatCurrency(p.recovered_amount)}
                          </div>
                          <div className="text-[10px] text-slate-400">Recovered Value</div>
                        </div>
                        <Badge
                          variant={isSuccess ? 'success' : 'secondary'}
                          className="text-xs px-2 py-0.5 flex items-center space-x-1"
                        >
                          {isSuccess ? (
                            <CheckCircle2 className="w-3 h-3 mr-1 text-emerald-600" />
                          ) : (
                            <XCircle className="w-3 h-3 mr-1 text-slate-400" />
                          )}
                          <span>{p.outcome}</span>
                        </Badge>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};
