import React from 'react';
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

export const RecoveryCaseDetailDrawer: React.FC<RecoveryCaseDetailDrawerProps> = ({
  caseDetail,
  isOpen,
  onClose,
}) => {
  if (!caseDetail) return null;

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-3xl max-h-[85vh] overflow-y-auto p-6">
        <DialogHeader>
          <div className="flex items-center justify-between pr-6">
            <div className="space-y-1">
              <DialogTitle className="text-lg font-bold text-slate-900 flex items-center space-x-2">
                <span>{RECOVERY_CASES_CONSTANTS.DRAWER.TITLE}</span>
                <span className="font-mono text-sm text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                  {caseDetail.id}
                </span>
              </DialogTitle>
              <DialogDescription>
                {RECOVERY_CASES_CONSTANTS.DRAWER.SUBTITLE}
              </DialogDescription>
            </div>
            <Badge
              variant={caseDetail.status === 'RECOVERED' ? 'success' : 'warning'}
              className="text-xs px-2.5 py-0.5"
            >
              {caseDetail.status}
            </Badge>
          </div>
        </DialogHeader>

        {/* Top Overview Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 my-4">
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200/70">
            <div className="text-[11px] font-semibold text-slate-500 uppercase">Customer</div>
            <div className="text-xs font-bold text-slate-900 mt-1 truncate">
              {caseDetail.customer_name}
            </div>
            <div className="text-[11px] text-slate-500 truncate">{caseDetail.customer_email}</div>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200/70">
            <div className="text-[11px] font-semibold text-slate-500 uppercase">Amount at Risk</div>
            <div className="text-sm font-bold text-slate-900 mt-1">
              {formatCurrency(caseDetail.amount_at_risk ?? caseDetail.leak_amount ?? 0)}
            </div>
            <div className="text-[11px] text-emerald-600 font-medium">
              Recovered: {formatCurrency(caseDetail.recovered_amount || 0)}
            </div>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200/70">
            <div className="text-[11px] font-semibold text-slate-500 uppercase">Payer Reliability</div>
            <div className="text-xs font-bold text-slate-900 mt-1">
              {((caseDetail.payer_reliability_score ?? 0.75) * 100).toFixed(0)}% Score
            </div>
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
          <TabsList className="grid grid-cols-2 w-64 mb-4">
            <TabsTrigger value="timeline">
              {RECOVERY_CASES_CONSTANTS.DRAWER.TIMELINE_TAB}
            </TabsTrigger>
            <TabsTrigger value="actions">
              {RECOVERY_CASES_CONSTANTS.DRAWER.ACTIONS_TAB}
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
                {caseDetail.timeline.map((step, idx) => (
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
                          {step.output_summary}
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
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};
