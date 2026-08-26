import { useQuery } from '@tanstack/react-query';
import { DashboardService } from '../../../api/generated';

export const useDashboardSummary = () => {
  return useQuery({
    queryKey: ['dashboard', 'summary'],
    queryFn: () => DashboardService.getDashboardSummary(),
    refetchInterval: 10000,
  });
};
