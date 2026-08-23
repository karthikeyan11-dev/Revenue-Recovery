import { useQuery } from '@tanstack/react-query';
import { SystemService, type HealthResponse } from '../generated';

export function useHealthQuery() {
  return useQuery<HealthResponse>({
    queryKey: ['system', 'health'],
    queryFn: () => SystemService.getHealth(),
    refetchInterval: 10000,
    retry: 1,
  });
}
