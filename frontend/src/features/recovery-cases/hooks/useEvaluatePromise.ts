import { useMutation, useQueryClient } from '@tanstack/react-query';
import { PromiseToPayService } from '../../../api/generated';
import type { PromiseEvaluationRequest } from '../../../api/generated';

export const useEvaluatePromise = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      promiseId,
      requestBody,
    }: {
      promiseId: string;
      requestBody: PromiseEvaluationRequest;
    }) =>
      PromiseToPayService.evaluatePromise(
        promiseId,
        requestBody
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cases'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};
