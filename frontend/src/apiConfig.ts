export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  HEALTH: `${API_BASE_URL}/health`,
  DASHBOARD_SUMMARY: `${API_BASE_URL}/dashboard/summary`,
  CASES: `${API_BASE_URL}/cases`,
  PROMISES: `${API_BASE_URL}/promises`,
  AGENTS_ACTIVITY: `${API_BASE_URL}/agents/activity`,
  DATA_GENERATE: `${API_BASE_URL}/data/generate`,
  RUN_BASELINE: `${API_BASE_URL}/run/baseline`,
  RUN_AI: `${API_BASE_URL}/run/ai`,
  WEBHOOKS_RAZORPAY: `${API_BASE_URL}/webhooks/razorpay`,
} as const;
