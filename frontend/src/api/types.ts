export interface HealthResponse {
  status: 'ok' | 'degraded' | 'error';
  service: string;
  database: string;
  error?: string;
  version: string;
}

export interface RootResponse {
  name: string;
  version: string;
  environment: string;
  docs_url: string;
  health_url: string;
}

export interface ApiError {
  message: string;
  status?: number;
  details?: unknown;
}
