import { useQuery } from '@tanstack/react-query';
import { RecoveryCasesService } from '../../../api/generated';
import type { CaseStatus } from '../../../api/generated';

export const useRecoveryCases = (params?: {
  status?: CaseStatus;
  limit?: number;
  offset?: number;
}) => {
  return useQuery({
    queryKey: ['cases', params],
    queryFn: () =>
      RecoveryCasesService.listRecoveryCases(
        params?.status,
        params?.limit || 100,
        params?.offset || 0
      ),
    refetchInterval: 10000,
  });
};
