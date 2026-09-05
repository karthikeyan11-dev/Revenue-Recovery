import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../../api/client';
import type { PlaybookStatsDetail } from '../../../types/api.types';

export function useGetPlaybookStats(isOpen: boolean, initialData?: PlaybookStatsDetail | null) {
  return useQuery({
    queryKey: ['agents', 'playbook-stats'],
    queryFn: () => apiClient.getPlaybookStats(),
    enabled: isOpen,
    initialData: initialData ?? undefined,
    staleTime: 10_000,
  });
}
