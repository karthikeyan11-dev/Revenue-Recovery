import React from 'react';
import { Database, CheckCircle2, XCircle, Zap, ShieldCheck, Layers, RefreshCw } from 'lucide-react';
import { SideDrawer } from '../../../components/ui/side-drawer';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { AGENT_ACTIVITY_CONSTANTS } from '../constants/agent-activity.constants';
import { useGetPlaybookStats } from '../hooks/useGetPlaybookStats';
import type { PlaybookStatsDetail } from '../../../types/api.types';

export interface PlaybookStatsDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  initialStats?: PlaybookStatsDetail | null;
}

export const PlaybookStatsDrawer: React.FC<PlaybookStatsDrawerProps> = ({
  isOpen,
  onClose,
  initialStats,
}) => {
  const { data: stats, isLoading, isFetching, refetch } = useGetPlaybookStats(isOpen, initialStats);

  const constants = AGENT_ACTIVITY_CONSTANTS.PLAYBOOK_DRAWER;
  const totalCases = stats?.total_cases ?? 0;
  const baselineCount = stats?.baseline_precedents ?? 0;
  const learnedCount = stats?.learned_cases ?? 0;

  return (
    <SideDrawer
      isOpen={isOpen}
      onClose={onClose}
      title={constants.TITLE}
      subtitle={constants.SUBTITLE}
      badge={
        <Badge variant="outline" className="bg-indigo-50 text-indigo-700 border-indigo-200 text-[11px] font-medium flex items-center space-x-1">
          <Database className="w-3 h-3 mr-1 text-indigo-600" />
          <span>{constants.BADGE_LABEL}</span>
        </Badge>
      }
      footer={
        <div className="flex items-center justify-between text-xs text-slate-500">
          <div className="flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>ChromaDB Vector Store Active</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => refetch()}
            disabled={isLoading || isFetching}
            className="h-7 px-2 text-xs text-indigo-600 hover:text-indigo-800 hover:bg-indigo-50"
          >
            {isFetching || isLoading ? (
              <img
                src="/revenue-recovery-logo-alone.png"
                alt="Loading"
                className="w-3.5 h-3.5 mr-1.5 animate-logo-pulse object-contain inline-block"
              />
            ) : (
              <RefreshCw className="w-3 h-3 mr-1" />
            )}
            <span>Refresh</span>
          </Button>
        </div>
      }
    >
      {/* 1. Top Summary Counters */}
      <div className="grid grid-cols-3 gap-2.5">
        <div className="p-3 bg-indigo-50/60 rounded-lg border border-indigo-100/80">
          <div className="text-[11px] font-semibold text-indigo-700 uppercase tracking-wider">
            {constants.TOTAL_STORED_LABEL}
          </div>
          <div className="text-xl font-extrabold text-indigo-950 mt-1">
            {totalCases}
          </div>
          <div className="text-[10px] text-indigo-600 font-medium mt-0.5">
            Vector Embeddings
          </div>
        </div>

        <div className="p-3 bg-slate-50 rounded-lg border border-slate-200/80">
          <div className="text-[11px] font-semibold text-slate-600 uppercase tracking-wider">
            {constants.BASELINE_LABEL}
          </div>
          <div className="text-xl font-extrabold text-slate-900 mt-1">
            {baselineCount}
          </div>
          <div className="text-[10px] text-slate-500 font-medium mt-0.5">
            Seeded Standards
          </div>
        </div>

        <div className="p-3 bg-emerald-50/70 rounded-lg border border-emerald-100">
          <div className="text-[11px] font-semibold text-emerald-700 uppercase tracking-wider">
            {constants.LEARNED_LABEL}
          </div>
          <div className="text-xl font-extrabold text-emerald-900 mt-1">
            {learnedCount}
          </div>
          <div className="text-[10px] text-emerald-600 font-medium mt-0.5">
            Auto-Accumulated
          </div>
        </div>
      </div>

      {/* 2. Failure Category Breakdown */}
      <div className="space-y-3">
        <div className="flex items-center justify-between border-b border-slate-100 pb-2">
          <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-1.5">
            <Layers className="w-3.5 h-3.5 text-slate-600" />
            <span>{constants.SECTION_FAILURES}</span>
          </h4>
          <span className="text-[11px] font-medium text-slate-500">
            {stats?.failure_reasons.length ?? 0} Categories
          </span>
        </div>

        <div className="border border-slate-200/90 rounded-lg overflow-hidden shadow-xs">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200/80 text-slate-600 font-semibold">
              <tr>
                <th className="py-2.5 px-3">{constants.FAILURE_REASON_COL}</th>
                <th className="py-2.5 px-3 text-right">{constants.PRECEDENT_CASES_COL}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700 bg-white">
              {stats?.failure_reasons && stats.failure_reasons.length > 0 ? (
                stats.failure_reasons.map((item) => {
                  const pct = totalCases > 0 ? Math.round((item.count / totalCases) * 100) : 0;
                  return (
                    <tr key={item.failure_reason} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-2.5 px-3.5 font-mono font-medium text-slate-800">
                        <div className="space-y-1">
                          <div className="flex items-center space-x-1.5">
                            <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
                            <span>{item.failure_reason}</span>
                          </div>
                          <div className="w-full bg-slate-100 h-1 rounded-full overflow-hidden">
                            <div
                              className="bg-indigo-500 h-full rounded-full transition-all duration-500"
                              style={{ width: `${pct}%` }}
                            />
                          </div>
                        </div>
                      </td>
                      <td className="py-2.5 px-3.5 text-right font-semibold text-slate-900 align-top">
                        <div className="flex items-center justify-end space-x-2">
                          <span className="text-sm font-bold text-slate-900">{item.count}</span>
                          <span className="text-[11px] text-slate-400 font-medium">({pct}%)</span>
                        </div>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={2} className="py-4 text-center text-slate-400">
                    {constants.EMPTY_BREAKDOWN}
                  </td>
                </tr>
              )}
            </tbody>
            {stats?.failure_reasons && stats.failure_reasons.length > 0 && (
              <tfoot className="bg-slate-50/90 border-t border-slate-200/80 font-bold text-slate-900">
                <tr>
                  <td className="py-2.5 px-3">{constants.TOTAL_LABEL}</td>
                  <td className="py-2.5 px-3 text-right text-indigo-700">{totalCases}</td>
                </tr>
              </tfoot>
            )}
          </table>
        </div>
      </div>

      {/* 3. Learned Outcomes & Actions */}
      <div className="space-y-3">
        <div className="border-b border-slate-100 pb-2">
          <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-slate-600" />
            <span>{constants.SECTION_OUTCOMES}</span>
          </h4>
        </div>

        {/* Outcomes Recorded */}
        <div className="p-3 bg-slate-50/80 rounded-lg border border-slate-200/80 space-y-2">
          <div className="text-[11px] font-semibold text-slate-600 uppercase tracking-wider">
            {constants.OUTCOMES_RECORDED}
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div className="p-2.5 bg-white rounded border border-emerald-100 flex items-center space-x-2.5 shadow-2xs">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              <div>
                <div className="text-[11px] text-slate-500 font-medium">{constants.RECOVERED_LABEL}</div>
                <div className="text-sm font-bold text-emerald-700">
                  {stats?.outcomes?.recovered_count ?? 0} <span className="text-[10px] text-slate-400 font-normal">cases</span>
                </div>
              </div>
            </div>

            <div className="p-2.5 bg-white rounded border border-slate-200 flex items-center space-x-2.5 shadow-2xs">
              <XCircle className="w-4 h-4 text-slate-400 shrink-0" />
              <div>
                <div className="text-[11px] text-slate-500 font-medium">{constants.FAILED_LABEL}</div>
                <div className="text-sm font-bold text-slate-800">
                  {stats?.outcomes?.failed_or_escalated_count ?? 0} <span className="text-[10px] text-slate-400 font-normal">cases</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Action Types Analyzed */}
        <div className="p-3 bg-slate-50/80 rounded-lg border border-slate-200/80 space-y-2">
          <div className="text-[11px] font-semibold text-slate-600 uppercase tracking-wider flex items-center justify-between">
            <span>{constants.ACTIONS_ANALYZED}</span>
            <Zap className="w-3.5 h-3.5 text-amber-500" />
          </div>
          <div className="space-y-1.5">
            {stats?.actions && stats.actions.length > 0 ? (
              stats.actions.map((act) => (
                <div
                  key={act.action}
                  className="flex items-center justify-between p-2 bg-white rounded border border-slate-200/70 text-xs shadow-2xs"
                >
                  <span className="font-mono font-medium text-slate-800">{act.action}</span>
                  <Badge variant="outline" className="bg-slate-50 text-slate-700 font-bold border-slate-200">
                    {act.count} cases
                  </Badge>
                </div>
              ))
            ) : (
              <div className="text-xs text-slate-400 py-1 text-center">
                {constants.EMPTY_BREAKDOWN}
              </div>
            )}
          </div>
        </div>
      </div>
    </SideDrawer>
  );
};
