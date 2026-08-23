import { useQuery } from '@tanstack/react-query';
import { AgentsService, type AgentActivityFeedResponse } from '../generated';

export function useAgentActivityQuery(limit = 50) {
  return useQuery<AgentActivityFeedResponse>({
    queryKey: ['agents', 'activity', limit],
    queryFn: () => AgentsService.getAgentActivityFeed(limit),
    refetchInterval: 5000,
  });
}
