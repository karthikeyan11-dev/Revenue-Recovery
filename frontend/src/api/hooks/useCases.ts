import { useQuery } from '@tanstack/react-query';
import {
  RecoveryCasesService,
  type CasesListResponse,
  type CaseStatus,
  type RecoveryCaseDetail,
} from '../generated';

export function useCasesQuery(params?: { status?: CaseStatus; limit?: number; offset?: number }) {
  return useQuery<CasesListResponse>({
    queryKey: ['cases', 'list', params],
    queryFn: () =>
      RecoveryCasesService.listRecoveryCases(params?.status, params?.limit, params?.offset),
  });
}

export function useCaseDetailQuery(caseId: string) {
  return useQuery<RecoveryCaseDetail>({
    queryKey: ['cases', 'detail', caseId],
    queryFn: () => RecoveryCasesService.getRecoveryCaseDetail(caseId),
    enabled: Boolean(caseId),
  });
}
