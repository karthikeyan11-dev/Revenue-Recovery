export const ROUTES = {
  OVERVIEW: 'overview',
  DASHBOARD: 'dashboard',
  CASES: 'cases',
  AGENTS: 'agents',
} as const;

export type RouteKey = (typeof ROUTES)[keyof typeof ROUTES];

export const NAV_ITEMS = [
  { key: ROUTES.OVERVIEW, label: 'System Health', id: 'nav-tab-overview' },
  { key: ROUTES.DASHBOARD, label: 'Dashboard', id: 'nav-tab-dashboard' },
  { key: ROUTES.CASES, label: 'Recovery Cases', id: 'nav-tab-cases' },
  { key: ROUTES.AGENTS, label: 'Agent Activity', id: 'nav-tab-agents' },
] as const;
