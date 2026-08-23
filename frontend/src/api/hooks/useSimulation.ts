import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  SimulationRunsService,
  type GenerateDataRequest,
  type GenerateDataResponse,
  type RunStrategyRequest,
  type RunStrategyResponse,
} from '../generated';

export function useGenerateDataMutation() {
  const queryClient = useQueryClient();
  return useMutation<GenerateDataResponse, Error, GenerateDataRequest>({
    mutationFn: (requestBody: GenerateDataRequest) =>
      SimulationRunsService.generateSyntheticData(requestBody),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cases'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    },
  });
}

export function useRunBaselineMutation() {
  const queryClient = useQueryClient();
  return useMutation<RunStrategyResponse, Error, RunStrategyRequest>({
    mutationFn: (requestBody: RunStrategyRequest) =>
      SimulationRunsService.runBaselineSimulation(requestBody),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

export function useRunAiSimulationMutation() {
  const queryClient = useQueryClient();
  return useMutation<RunStrategyResponse, Error, RunStrategyRequest>({
    mutationFn: (requestBody: RunStrategyRequest) =>
      SimulationRunsService.runAiOrchestratorSimulation(requestBody),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cases'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    },
  });
}
