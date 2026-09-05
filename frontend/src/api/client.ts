import type {
  DashboardMetricsResponse,
  RecoveryDiagnosticResponse,
  CasesListResponse,
  RecoveryCaseDetail,
  AgentActivityFeedResponse,
  AnalyticsBreakdownResponse,
  SimulationHistoryResponse,
  RunStrategyResponse,
  CustomersListResponse,
  PlaybookStatsDetail,
} from '../types/api.types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function fetchJson<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API Error ${res.status}: ${errorText || res.statusText}`);
  }

  return res.json() as Promise<T>;
}

export const apiClient = {
  // 1. Dashboard
  getDashboardSummary: (params?: { time_range?: string; date_from?: string; date_to?: string }) => {
    const query = new URLSearchParams();
    if (params?.time_range) query.set('time_range', params.time_range);
    if (params?.date_from) query.set('date_from', params.date_from);
    if (params?.date_to) query.set('date_to', params.date_to);
    const qs = query.toString();
    return fetchJson<DashboardMetricsResponse>(`/dashboard/summary${qs ? `?${qs}` : ''}`);
  },

  getDashboardDiagnostics: (params?: {
    time_range?: string;
    date_from?: string;
    date_to?: string;
    force_refresh?: boolean;
  }) => {
    const query = new URLSearchParams();
    if (params?.time_range) query.set('time_range', params.time_range);
    if (params?.date_from) query.set('date_from', params.date_from);
    if (params?.date_to) query.set('date_to', params.date_to);
    if (params?.force_refresh) query.set('force_refresh', 'true');
    const qs = query.toString();
    return fetchJson<RecoveryDiagnosticResponse>(`/dashboard/diagnostics${qs ? `?${qs}` : ''}`);
  },

  // 2. Recovery Cases
  getRecoveryCases: (params?: {
    status?: string;
    segment?: string;
    priority?: string;
    reason?: string;
    search?: string;
    date_from?: string;
    date_to?: string;
    limit?: number;
    offset?: number;
  }) => {
    const query = new URLSearchParams();
    if (params?.status && params.status !== 'all') query.set('status', params.status);
    if (params?.segment && params.segment !== 'all') query.set('segment', params.segment);
    if (params?.priority && params.priority !== 'all') query.set('priority', params.priority);
    if (params?.reason && params.reason !== 'all') query.set('reason', params.reason);
    if (params?.search) query.set('search', params.search);
    if (params?.date_from) query.set('date_from', params.date_from);
    if (params?.date_to) query.set('date_to', params.date_to);
    if (params?.limit !== undefined) query.set('limit', String(params.limit));
    if (params?.offset !== undefined) query.set('offset', String(params.offset));
    const qs = query.toString();
    return fetchJson<CasesListResponse>(`/cases${qs ? `?${qs}` : ''}`);
  },

  getRecoveryCaseDetail: (caseId: string) =>
    fetchJson<RecoveryCaseDetail>(`/cases/${encodeURIComponent(caseId)}`),

  // 3. Agent Activity
  getAgentActivity: (params?: {
    agent?: string;
    status?: string;
    search?: string;
    time_range?: string;
    limit?: number;
    offset?: number;
  }) => {
    const query = new URLSearchParams();
    if (params?.agent && params.agent !== 'all') query.set('agent', params.agent);
    if (params?.status && params.status !== 'all') query.set('status', params.status);
    if (params?.search) query.set('search', params.search);
    if (params?.time_range) query.set('time_range', params.time_range);
    if (params?.limit !== undefined) query.set('limit', String(params.limit));
    if (params?.offset !== undefined) query.set('offset', String(params.offset));
    const qs = query.toString();
    return fetchJson<AgentActivityFeedResponse>(`/agents/activity${qs ? `?${qs}` : ''}`);
  },

  getPlaybookStats: () =>
    fetchJson<PlaybookStatsDetail>('/agents/playbook/stats'),

  // 4. Analytics
  getAnalyticsBreakdown: (params?: { time_range?: string }) => {
    const query = new URLSearchParams();
    if (params?.time_range) query.set('time_range', params.time_range);
    const qs = query.toString();
    return fetchJson<AnalyticsBreakdownResponse>(`/analytics/breakdown${qs ? `?${qs}` : ''}`);
  },

  // 5. Simulations
  getSimulationHistory: (limit: number = 10) =>
    fetchJson<SimulationHistoryResponse>(`/simulations/history?limit=${limit}`),

  runBaselineSimulation: (payload: { limit?: number; simulation_name?: string }) =>
    fetchJson<RunStrategyResponse>('/run/baseline', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  runAiSimulation: (payload: { limit?: number; use_mock_llm?: boolean; simulation_name?: string }) =>
    fetchJson<RunStrategyResponse>('/run/ai', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  generateData: (payload: { transaction_count: number; failure_rate: number }) =>
    fetchJson<{ transactions_generated: number; failures_generated: number; message: string }>(
      '/data/generate',
      {
        method: 'POST',
        body: JSON.stringify(payload),
      }
    ),

  // 6. Customers
  getCustomers: (params?: {
    search?: string;
    segment?: string;
    risk_level?: string;
    limit?: number;
    offset?: number;
  }) => {
    const query = new URLSearchParams();
    if (params?.search) query.set('search', params.search);
    if (params?.segment && params.segment !== 'all') query.set('segment', params.segment);
    if (params?.risk_level && params.risk_level !== 'all') query.set('risk_level', params.risk_level);
    if (params?.limit !== undefined) query.set('limit', String(params.limit));
    if (params?.offset !== undefined) query.set('offset', String(params.offset));
    const qs = query.toString();
    return fetchJson<CustomersListResponse>(`/customers${qs ? `?${qs}` : ''}`);
  },
};
