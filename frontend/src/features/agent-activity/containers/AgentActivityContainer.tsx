import React, { useState } from 'react';
import { Activity, RefreshCw } from 'lucide-react';
import { useAgentActivityFeed } from '../hooks/useAgentActivityFeed';
import { ActivityFeed } from '../components/ActivityFeed';
import type { AgentActivityItem } from '../../../types/agent';

export const AgentActivityContainer: React.FC = () => {
  const [selectedAgent, setSelectedAgent] = useState<string>('ALL');
  const [filterDecision, setFilterDecision] = useState<string>('ALL');

  const { data: activityData, isLoading, isFetching, refetch } = useAgentActivityFeed(60);

  const activities: AgentActivityItem[] = activityData?.activities || [];

  const filteredActivities = activities.filter((act: AgentActivityItem) => {
    if (selectedAgent !== 'ALL' && act.agent !== selectedAgent) return false;
    if (filterDecision === 'POLICY_REJECTIONS' && act.decision !== 'REJECTED') return false;
    if (filterDecision === 'POLICY_ESCALATIONS' && act.decision !== 'ESCALATED') return false;
    if (filterDecision === 'RECOVERIES' && act.decision !== 'RECOVERED') return false;
    return true;
  });

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Header & Filter Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-[#0c2340]/90 border border-slate-800 backdrop-blur shadow-xl">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <Activity className="w-5 h-5 text-brand-400" />
            <span>Multi-Agent Live Activity Feed & Chain-of-Thought Audit</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real-time trace logs showing Revenue Detective, Customer Intelligence, Recovery Strategist, and Policy Engine decisions with Laplace smoothed confidence metrics.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Agent Selector */}
          <select
            value={selectedAgent}
            onChange={(e) => setSelectedAgent(e.target.value)}
            className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
          >
            <option value="ALL">All Agents</option>
            <option value="Revenue Detective">Revenue Detective</option>
            <option value="Customer Intelligence">Customer Intelligence</option>
            <option value="Recovery Strategist">Recovery Strategist</option>
            <option value="Policy Engine">Policy Engine</option>
            <option value="Action Executor">Action Executor</option>
          </select>

          {/* Decision Outcome Filter */}
          <select
            value={filterDecision}
            onChange={(e) => setFilterDecision(e.target.value)}
            className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
          >
            <option value="ALL">All Outcomes</option>
            <option value="POLICY_REJECTIONS">Policy Rejected</option>
            <option value="POLICY_ESCALATIONS">Human Escalations</option>
            <option value="RECOVERIES">Recovered / Approved</option>
          </select>

          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition disabled:opacity-50"
            title="Refresh stream"
          >
            <RefreshCw className={`w-4 h-4 ${isFetching ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Activity Feed List */}
      <ActivityFeed activities={filteredActivities} isLoading={isLoading} />
    </div>
  );
};
