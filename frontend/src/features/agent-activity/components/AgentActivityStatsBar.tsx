import React, { useState } from 'react';
import { Bot, Layers, Zap, CheckCircle2, Database, ChevronRight } from 'lucide-react';
import { Card, CardContent } from '../../../components/ui/card';
import { formatPercent } from '../../../lib/utils';
import { AGENT_ACTIVITY_CONSTANTS } from '../constants/agent-activity.constants';
import { PlaybookStatsDrawer } from './PlaybookStatsDrawer';
import type { AgentActivityStatsBarProps } from '../types/agent-activity.types';

export const AgentActivityStatsBar: React.FC<AgentActivityStatsBarProps> = ({ stats }) => {
  const [isPlaybookDrawerOpen, setIsPlaybookDrawerOpen] = useState(false);
  const precedentCount = stats.playbook_precedent_count ?? 40;
  const learnedCount = stats.playbook_learned_cases_count ?? 0;
  const statLabels = AGENT_ACTIVITY_CONSTANTS.STATS;
  const drawerLabels = AGENT_ACTIVITY_CONSTANTS.PLAYBOOK_DRAWER;

  return (
    <>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {/* 1. Active Agents */}
        <Card className="bg-white border-slate-200/80 shadow-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between text-xs text-slate-500 font-semibold uppercase">
              <span>{statLabels.ACTIVE_AGENTS}</span>
              <Bot className="w-4 h-4 text-blue-600" />
            </div>
            <div className="mt-2 text-xl font-bold text-slate-900">
              {stats.active_agents_count}/{stats.total_agents_count}
            </div>
            <div className="text-[11px] text-emerald-600 font-medium mt-0.5 flex items-center space-x-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              <span>{statLabels.ALL_AGENTS_ONLINE}</span>
            </div>
          </CardContent>
        </Card>

        {/* 2. RAG Knowledge Store (ChromaDB Memory - Clickable for side drawer) */}
        <Card
          onClick={() => setIsPlaybookDrawerOpen(true)}
          className="bg-white border-slate-200/80 shadow-sm hover:border-indigo-300 hover:shadow-md hover:bg-indigo-50/20 cursor-pointer transition-all group relative"
          title={drawerLabels.CLICK_TO_INSPECT}
        >
          <CardContent className="p-4">
            <div className="flex items-center justify-between text-xs text-slate-500 font-semibold uppercase">
              <span className="group-hover:text-indigo-700 transition-colors">{statLabels.RAG_PLAYBOOK_STORE}</span>
              <div className="flex items-center space-x-1">
                <Database className="w-4 h-4 text-indigo-600 group-hover:scale-110 transition-transform" />
                <ChevronRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-indigo-600 transition-colors" />
              </div>
            </div>
            <div className="mt-2 text-xl font-bold text-indigo-700 flex items-baseline space-x-1">
              <span>{precedentCount}</span>
              <span className="text-xs font-medium text-slate-500">{statLabels.CASES_LABEL}</span>
            </div>
            <div className="text-[11px] text-indigo-600 font-medium mt-0.5 flex items-center justify-between">
              <span>{learnedCount > 0 ? `+${learnedCount} ${drawerLabels.LEARNED_LABEL}` : statLabels.PERSISTENT_MEMORY_ACTIVE}</span>
              <span className="text-[10px] text-indigo-500 underline opacity-0 group-hover:opacity-100 transition-opacity">View Details</span>
            </div>
          </CardContent>
        </Card>

        {/* 3. Actions Today */}
        <Card className="bg-white border-slate-200/80 shadow-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between text-xs text-slate-500 font-semibold uppercase">
              <span>{statLabels.ACTIONS_TODAY}</span>
              <Zap className="w-4 h-4 text-purple-600" />
            </div>
            <div className="mt-2 text-xl font-bold text-slate-900">
              {stats.actions_today_count}
            </div>
            <div className="text-[11px] text-slate-500 font-medium mt-0.5">
              {statLabels.AUTONOMOUS_DECISIONS}
            </div>
          </CardContent>
        </Card>

        {/* 4. Success Rate */}
        <Card className="bg-white border-slate-200/80 shadow-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between text-xs text-slate-500 font-semibold uppercase">
              <span>{statLabels.SUCCESS_RATE}</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            </div>
            <div className="mt-2 text-xl font-bold text-slate-900">
              {formatPercent(stats.success_rate_percent)}
            </div>
            <div className="text-[11px] text-emerald-600 font-medium mt-0.5">
              {statLabels.EMPIRICAL_ACCURACY}
            </div>
          </CardContent>
        </Card>

        {/* 5. Active Cases */}
        <Card className="bg-white border-slate-200/80 shadow-sm col-span-2 md:col-span-1">
          <CardContent className="p-4">
            <div className="flex items-center justify-between text-xs text-slate-500 font-semibold uppercase">
              <span>{statLabels.ACTIVE_CASES}</span>
              <Layers className="w-4 h-4 text-amber-600" />
            </div>
            <div className="mt-2 text-xl font-bold text-slate-900">
              {stats.active_cases_count}
            </div>
            <div className="text-[11px] text-slate-500 font-medium mt-0.5">
              {statLabels.IN_ACTIVE_RECOVERY}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* RAG Knowledge Store Slide-Over Side Drawer */}
      <PlaybookStatsDrawer
        isOpen={isPlaybookDrawerOpen}
        onClose={() => setIsPlaybookDrawerOpen(false)}
      />
    </>
  );
};
