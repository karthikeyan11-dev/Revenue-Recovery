import { useQuery } from '@tanstack/react-query';
import { DashboardService, type DashboardMetricsResponse } from '../generated';

export function useDashboardQuery() {
  return useQuery<DashboardMetricsResponse>({
    queryKey: ['dashboard', 'summary'],
    queryFn: () => DashboardService.getDashboardSummary(),
    refetchInterval: 15000,
  });
}
