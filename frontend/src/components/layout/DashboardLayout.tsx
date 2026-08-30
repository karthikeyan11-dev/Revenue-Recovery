import React from 'react';
import {
  LayoutDashboard,
  FileText,
  Bot,
  TrendingUp,
  FlaskConical,
  Users,
  Settings,
  ChevronDown,
  Download,
  PlayCircle,
} from 'lucide-react';
import { APP_CONSTANTS } from '../../constants/app.constants';
import { NAV_ITEMS, ROUTES } from '../../constants/routes.constants';
import type { RouteKey } from '../../constants/routes.constants';
import { Button } from '../ui/button';

export interface DashboardLayoutProps {
  activeTab: RouteKey;
  onTabChange: (tab: RouteKey) => void;
  timeRange?: string;
  onTimeRangeChange?: (range: string) => void;
  children: React.ReactNode;
  onActionClick?: () => void;
}

const ICON_MAP = {
  LayoutDashboard: LayoutDashboard,
  FileText: FileText,
  Bot: Bot,
  TrendingUp: TrendingUp,
  FlaskConical: FlaskConical,
  Users: Users,
  Settings: Settings,
};

const PAGE_METADATA: Record<
  RouteKey,
  { title: string; subtitle: string; actionLabel?: string; actionIcon?: 'download' | 'play' }
> = {
  [ROUTES.DASHBOARD]: {
    title: 'Dashboard',
    subtitle: 'AI Revenue Recovery Orchestrator Overview',
    actionLabel: APP_CONSTANTS.EXPORT_REPORT_BUTTON,
    actionIcon: 'download',
  },
  [ROUTES.CASES]: {
    title: 'Recovery Cases',
    subtitle: 'View and manage all failed payment recovery cases',
    actionLabel: APP_CONSTANTS.EXPORT_BUTTON,
    actionIcon: 'download',
  },
  [ROUTES.AGENTS]: {
    title: 'Agent Activity',
    subtitle: 'Monitor live agent operations and activity across all recovery cases',
    actionLabel: APP_CONSTANTS.EXPORT_LOGS_BUTTON,
    actionIcon: 'download',
  },
  [ROUTES.SETTINGS]: {
    title: 'Settings & Policy Guardrails',
    subtitle: 'Configure deterministic policy rules, webhooks, and thresholds',
    actionLabel: 'Save Preferences',
  },
};

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  activeTab,
  onTabChange,
  children,
  onActionClick,
}) => {
  const currentMeta = PAGE_METADATA[activeTab] || PAGE_METADATA[ROUTES.DASHBOARD];

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-900 flex font-sans">
      {/* Fixed Left Sidebar */}
      <aside className="w-64 bg-gradient-to-b from-slate-900 via-[#0c2340] to-slate-900 text-white border-r border-slate-800/80 flex flex-col justify-between shrink-0 fixed inset-y-0 left-0 z-30 shadow-xl">
        <div>
          {/* Brand Header */}
          <div className="h-16 flex items-center px-5 border-b border-slate-800/80">
            <div className="flex items-center space-x-2.5">
              <img
                src="/revenue-recovery-logo-alone.png"
                alt="Revenue Recovery Logo"
                className="w-8 h-8 object-contain drop-shadow-md"
              />
              <span className="text-base font-extrabold text-white tracking-tight">
                {APP_CONSTANTS.BRAND_NAME}
              </span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-3 space-y-1">
            {NAV_ITEMS.map((item) => {
              const Icon = ICON_MAP[item.iconName];
              const isActive = activeTab === item.key;
              return (
                <button
                  key={item.key}
                  id={item.id}
                  onClick={() => onTabChange(item.key)}
                  className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-white/15 backdrop-blur-md text-white font-semibold border border-white/25 shadow-lg shadow-black/20 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.25)]'
                      : 'text-slate-300 hover:bg-white/5 hover:text-white border border-transparent'
                  }`}
                >
                  <Icon
                    className={`w-4 h-4 transition-colors ${
                      isActive
                        ? 'text-white drop-shadow-[0_0_6px_rgba(255,255,255,0.5)]'
                        : 'text-slate-400'
                    }`}
                  />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Sidebar Footer */}
        <div className="p-4 space-y-3 border-t border-slate-800/80">
          {/* System Status Pill */}
          <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800">
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-xs font-semibold text-slate-200">System Status</span>
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5 ml-4">
              {APP_CONSTANTS.SYSTEM_STATUS}
            </p>
          </div>

          {/* User Profile */}
          <div className="flex items-center justify-between pt-1">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-full bg-brand-600/90 border border-brand-500/30 text-white flex items-center justify-center text-xs font-bold shadow-sm">
                {APP_CONSTANTS.USER_INITIALS}
              </div>
              <div className="flex flex-col">
                <span className="text-xs font-semibold text-slate-200 leading-tight">
                  {APP_CONSTANTS.USER_NAME}
                </span>
                <span className="text-[11px] text-slate-400 leading-tight">
                  {APP_CONSTANTS.USER_ROLE}
                </span>
              </div>
            </div>
            <ChevronDown className="w-4 h-4 text-slate-400" />
          </div>
        </div>
      </aside>

      {/* Main Content Area (offset by sidebar width) */}
      <div className="flex-1 pl-64 flex flex-col min-w-0">
        {/* Top Header */}
        <header className="h-20 bg-[#f8fafc] px-8 flex items-center justify-between sticky top-0 z-20">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              {currentMeta.title}
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">{currentMeta.subtitle}</p>
          </div>

          <div className="flex items-center space-x-3">
            {/* Active Cohort Badge */}
            <div className="flex items-center space-x-2 px-3 py-1.5 bg-white border border-slate-200/90 rounded-lg shadow-xs">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-xs font-semibold text-slate-800 tracking-tight">
                Current Batch:
              </span>
              <span className="text-xs font-medium text-slate-500">
                100 Transactions (Active Cohort)
              </span>
            </div>

            {/* Action Button */}
            {currentMeta.actionLabel && (
              <Button
                variant="outline"
                size="sm"
                onClick={onActionClick}
                className="bg-white border-slate-200 text-slate-700 hover:bg-slate-50 shadow-sm text-xs font-medium flex items-center space-x-1.5 h-9 px-3.5"
              >
                {currentMeta.actionIcon === 'download' && <Download className="w-3.5 h-3.5 text-slate-500" />}
                {currentMeta.actionIcon === 'play' && <PlayCircle className="w-3.5 h-3.5 text-blue-600" />}
                <span>{currentMeta.actionLabel}</span>
              </Button>
            )}
          </div>
        </header>

        {/* Page Content Body */}
        <main className="flex-1 px-8 pb-12 min-w-0 max-w-[1600px] w-full mx-auto">{children}</main>
      </div>
    </div>
  );
};
