import { useQuery } from '@tanstack/react-query';
import { AgentsService } from '../../../api/generated';

export const useAgentActivityFeed = (limit: number = 60) => {
  return useQuery({
    queryKey: ['agents', 'activity', limit],
    queryFn: () => AgentsService.getAgentActivityFeed(limit),
    refetchInterval: 5000,
  });
};
