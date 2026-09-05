import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../../api/client';
import type { AgentActivityFiltersState } from '../types/agent-activity.types';

export function useGetAgentActivity(filters: AgentActivityFiltersState) {
  return useQuery({
    queryKey: ['agents', 'activity', filters],
    queryFn: () =>
      apiClient.getAgentActivity({
        agent: filters.agent !== 'all' ? filters.agent : undefined,
        status: filters.status !== 'all' ? filters.status : undefined,
        time_range: filters.time_range !== 'all' ? filters.time_range : undefined,
        search: filters.search || undefined,
        limit: 50,
      }),
    staleTime: 5_000,
    refetchInterval: 15_000,
  });
}
