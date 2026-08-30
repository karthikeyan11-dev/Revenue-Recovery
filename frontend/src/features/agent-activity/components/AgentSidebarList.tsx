import React from 'react';
import { Bot } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { AGENT_ACTIVITY_CONSTANTS } from '../constants/agent-activity.constants';
import type { AgentSidebarListProps } from '../types/agent-activity.types';

export const AgentSidebarList: React.FC<AgentSidebarListProps> = ({
  agents,
  selectedAgent,
  onSelectAgent,
}) => {
  return (
    <Card className="bg-white border-slate-200/80 shadow-sm">
      <CardHeader className="pb-3 border-b border-slate-100">
        <CardTitle className="text-sm font-bold text-slate-900">
          {AGENT_ACTIVITY_CONSTANTS.SIDEBAR_TITLE}
        </CardTitle>
      </CardHeader>
      <CardContent className="p-2 space-y-1">
        {/* All Agents Option */}
        <button
          onClick={() => onSelectAgent('all')}
          className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
            selectedAgent === 'all'
              ? 'bg-blue-50 text-blue-700 font-semibold'
              : 'text-slate-700 hover:bg-slate-50'
          }`}
        >
          <div className="flex items-center space-x-2.5">
            <div
              className={`w-6 h-6 rounded-md flex items-center justify-center ${
                selectedAgent === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-100 text-slate-500'
              }`}
            >
              <Bot className="w-3.5 h-3.5" />
            </div>
            <span>{AGENT_ACTIVITY_CONSTANTS.ALL_AGENTS}</span>
          </div>
          <span className="text-[10px] text-slate-400 font-semibold">6</span>
        </button>

        {/* Individual Agents */}
        {agents.map((agent) => {
          const isSelected = selectedAgent === agent.name;
          return (
            <button
              key={agent.name}
              onClick={() => onSelectAgent(agent.name)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                isSelected
                  ? 'bg-blue-50 text-blue-700 font-semibold'
                  : 'text-slate-700 hover:bg-slate-50'
              }`}
            >
              <div className="flex items-center space-x-2.5">
                <div
                  className={`w-6 h-6 rounded-md flex items-center justify-center ${
                    isSelected
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-100 text-slate-500'
                  }`}
                >
                  <Bot className="w-3.5 h-3.5" />
                </div>
                <div className="text-left">
                  <div className="font-semibold text-slate-900 leading-tight">{agent.name}</div>
                  <div className="text-[10px] text-emerald-600 flex items-center space-x-1 mt-0.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                    <span>{agent.status}</span>
                  </div>
                </div>
              </div>
            </button>
          );
        })}
      </CardContent>
    </Card>
  );
};
