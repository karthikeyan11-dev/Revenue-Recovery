import React from 'react';
import { Activity } from 'lucide-react';
import type { AgentActivityItem } from '../../../types/agent';
import { AgentReasoningCard } from './AgentReasoningCard';

export interface ActivityFeedProps {
  activities: AgentActivityItem[];
  isLoading: boolean;
}

export const ActivityFeed: React.FC<ActivityFeedProps> = ({ activities, isLoading }) => {
  if (isLoading) {
    return (
      <div className="py-20 text-center text-slate-500 rounded-2xl bg-[#0c2340]/60 border border-slate-800">
        <Activity className="w-8 h-8 animate-spin mx-auto mb-3 text-brand-400" />
        <p className="text-sm">Connecting to agent real-time decision stream...</p>
      </div>
    );
  }

  if (activities.length === 0) {
    return (
      <div className="py-16 text-center text-slate-500 rounded-2xl bg-[#0c2340]/60 border border-slate-800 text-sm italic">
        No agent activities logged yet. Run AI simulation from Dashboard to generate real-time multi-agent reasoning logs.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {activities.map((act) => (
        <AgentReasoningCard key={act.id} activity={act} />
      ))}
    </div>
  );
};
