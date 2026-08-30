export const ROUTES = {
  DASHBOARD: 'dashboard',
  CASES: 'cases',
  AGENTS: 'agents',
  SETTINGS: 'settings',
} as const;

export type RouteKey = (typeof ROUTES)[keyof typeof ROUTES];

export interface NavItemConfig {
  key: RouteKey;
  label: string;
  id: string;
  iconName: 'LayoutDashboard' | 'FileText' | 'Bot' | 'Settings';
}

export const NAV_ITEMS: NavItemConfig[] = [
  { key: ROUTES.DASHBOARD, label: 'Dashboard', id: 'nav-tab-dashboard', iconName: 'LayoutDashboard' },
  { key: ROUTES.CASES, label: 'Recovery Cases', id: 'nav-tab-cases', iconName: 'FileText' },
  { key: ROUTES.AGENTS, label: 'Agent Activity', id: 'nav-tab-agents', iconName: 'Bot' },
  { key: ROUTES.SETTINGS, label: 'Settings', id: 'nav-tab-settings', iconName: 'Settings' },
];

