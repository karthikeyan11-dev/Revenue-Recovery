import { useQuery } from '@tanstack/react-query';
import { RecoveryCasesService } from '../../../api/generated';

export const useRecoveryCaseDetail = (caseId: string) => {
  return useQuery({
    queryKey: ['cases', 'detail', caseId],
    queryFn: () => RecoveryCasesService.getRecoveryCaseDetail(caseId),
    enabled: Boolean(caseId),
  });
};
