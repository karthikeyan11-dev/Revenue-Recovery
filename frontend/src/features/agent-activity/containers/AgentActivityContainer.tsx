import React, { useState } from 'react';
import { RefreshCw, AlertTriangle } from 'lucide-react';
import { Button } from '../../../components/ui/button';
import { AgentActivityFeed } from '../components/AgentActivityFeed';
import { AgentActivityFilters } from '../components/AgentActivityFilters';
import { AgentActivityStatsBar } from '../components/AgentActivityStatsBar';
import { AgentSidebarList } from '../components/AgentSidebarList';
import { useGetAgentActivity } from '../hooks/useGetAgentActivity';
import { LogoLoader } from '../../../components/common/LogoLoader';
import type { AgentActivityFiltersState } from '../types/agent-activity.types';

const INITIAL_FILTERS: AgentActivityFiltersState = {
  agent: 'all',
  status: 'all',
  time_range: 'all',
  search: '',
};

export const AgentActivityContainer: React.FC = () => {
  const [filters, setFilters] = useState<AgentActivityFiltersState>(INITIAL_FILTERS);
  const { data, isLoading, isError, error, refetch } = useGetAgentActivity(filters);

  const handleFilterChange = (key: keyof AgentActivityFiltersState, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const handleResetFilters = () => {
    setFilters(INITIAL_FILTERS);
  };

  const handleSelectAgent = (agentName: string) => {
    setFilters((prev) => ({ ...prev, agent: agentName }));
  };

  if (isError) {
    return (
      <div className="p-8 bg-white border border-rose-200 rounded-xl shadow-sm text-center space-y-4">
        <div className="w-12 h-12 rounded-full bg-rose-50 text-rose-600 flex items-center justify-center mx-auto">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <div className="text-base font-semibold text-slate-900">Failed to load Agent Activity</div>
        <p className="text-xs text-slate-500 max-w-md mx-auto">
          {(error as Error)?.message || 'An unexpected error occurred.'}
        </p>
        <Button onClick={() => refetch()} variant="outline" size="sm" className="space-x-2">
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Retry Connection</span>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 1. Headline Telemetry Bar */}
      {data?.stats && <AgentActivityStatsBar stats={data.stats} />}

      {/* 2. Main Content Grid (Left Agent List + Right Activity Stream) */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left Sub-Sidebar */}
        <div className="lg:col-span-1">
          <AgentSidebarList
            agents={data?.stats.agent_statuses || []}
            selectedAgent={filters.agent}
            onSelectAgent={handleSelectAgent}
          />
        </div>

        {/* Right Feed Area */}
        <div className="lg:col-span-3 space-y-4">
          <AgentActivityFilters
            filters={filters}
            onFilterChange={handleFilterChange}
            onResetFilters={handleResetFilters}
          />

          {isLoading ? (
            <LogoLoader variant="table" label="Streaming live agent decision ledger..." />
          ) : (
            <AgentActivityFeed
              activities={data?.activities || []}
              totalEvents={data?.total_events || 0}
            />
          )}
        </div>
      </div>
    </div>
  );
};
