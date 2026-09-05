import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../../api/client';
import type { RecoveryCasesFiltersState } from '../types/recovery-cases.types';

export function useGetRecoveryCases(
  filters: RecoveryCasesFiltersState,
  page: number = 1,
  pageSize: number = 10,
  selectedCaseId: string | null = null
) {
  const casesQuery = useQuery({
    queryKey: ['cases', 'list', filters, page, pageSize],
    queryFn: () =>
      apiClient.getRecoveryCases({
        search: filters.search || undefined,
        status: filters.status !== 'all' ? filters.status : undefined,
        priority: filters.priority !== 'all' ? filters.priority : undefined,
        reason: filters.reason !== 'all' ? filters.reason : undefined,
        limit: pageSize,
        offset: (page - 1) * pageSize,
      }),
    staleTime: 10_000,
    refetchInterval: 30_000,
  });

  const caseDetailQuery = useQuery({
    queryKey: ['cases', 'detail', selectedCaseId],
    queryFn: () => (selectedCaseId ? apiClient.getRecoveryCaseDetail(selectedCaseId) : null),
    enabled: !!selectedCaseId,
    staleTime: 15_000,
  });

  return {
    casesData: casesQuery.data,
    caseDetail: caseDetailQuery.data,
    isLoading: casesQuery.isLoading,
    isDetailLoading: caseDetailQuery.isLoading,
    isError: casesQuery.isError,
    error: casesQuery.error,
    refetch: casesQuery.refetch,
  };
}
