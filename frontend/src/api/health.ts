import { apiClient } from './client';
import type { HealthResponse, RootResponse } from './types';

export const healthApi = {
  getHealth: (): Promise<HealthResponse> => apiClient.get<HealthResponse>('/health'),
  getRoot: (): Promise<RootResponse> => apiClient.get<RootResponse>('/'),
};
