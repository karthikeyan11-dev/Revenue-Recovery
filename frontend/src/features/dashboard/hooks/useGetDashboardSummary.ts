import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../../api/client';

export function useGetDashboardSummary(timeRange?: string) {
  const summaryQuery = useQuery({
    queryKey: ['dashboard', 'summary', { timeRange }],
    queryFn: () => apiClient.getDashboardSummary({ time_range: timeRange }),
    staleTime: 10_000,
    refetchInterval: 30_000,
  });

  const recentCasesQuery = useQuery({
    queryKey: ['cases', 'recent', { limit: 5 }],
    queryFn: () => apiClient.getRecoveryCases({ limit: 5 }),
    staleTime: 10_000,
    refetchInterval: 30_000,
  });

  return {
    metrics: summaryQuery.data,
    recentCases: recentCasesQuery.data?.items || [],
    isLoading: summaryQuery.isLoading || recentCasesQuery.isLoading,
    isError: summaryQuery.isError || recentCasesQuery.isError,
    error: summaryQuery.error || recentCasesQuery.error,
    refetch: () => {
      summaryQuery.refetch();
      recentCasesQuery.refetch();
    },
  };
}
