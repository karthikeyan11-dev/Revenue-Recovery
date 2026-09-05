import type {
  AgentActivityItem,
  AgentActivityStats,
  AgentStatusInfo,
} from '../../../types/api.types';

export interface AgentActivityFiltersState {
  agent: string;
  status: string;
  time_range: string;
  search: string;
}

export interface AgentActivityStatsBarProps {
  stats: AgentActivityStats;
}

export interface AgentSidebarListProps {
  agents: AgentStatusInfo[];
  selectedAgent: string;
  onSelectAgent: (agentName: string) => void;
}

export interface AgentActivityFiltersProps {
  filters: AgentActivityFiltersState;
  onFilterChange: (key: keyof AgentActivityFiltersState, value: string) => void;
  onResetFilters: () => void;
}

export interface AgentActivityFeedProps {
  activities: AgentActivityItem[];
  totalEvents: number;
}
