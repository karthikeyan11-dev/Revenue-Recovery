import React, { useState, useEffect, useCallback } from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from './lib/queryClient';
import { DashboardLayout } from './components/layout/DashboardLayout';
import { DashboardContainer } from './features/dashboard';
import { RecoveryCasesContainer } from './features/recovery-cases';
import { AgentActivityContainer } from './features/agent-activity';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './components/ui/card';
import { ROUTES } from './constants/routes.constants';
import type { RouteKey } from './constants/routes.constants';

const PATH_TO_ROUTE: Record<string, RouteKey> = {
  '/': ROUTES.DASHBOARD,
  '/dashboard': ROUTES.DASHBOARD,
  '/recovery-cases': ROUTES.CASES,
  '/cases': ROUTES.CASES,
  '/agent-activity': ROUTES.AGENTS,
  '/agents': ROUTES.AGENTS,
  '/settings': ROUTES.SETTINGS,
};

const ROUTE_TO_PATH: Record<RouteKey, string> = {
  [ROUTES.DASHBOARD]: '/dashboard',
  [ROUTES.CASES]: '/recovery-cases',
  [ROUTES.AGENTS]: '/agent-activity',
  [ROUTES.SETTINGS]: '/settings',
};

const SettingsView: React.FC = () => (
  <div className="space-y-6">
    <Card className="bg-white border-slate-200/80 shadow-sm">
      <CardHeader>
        <CardTitle>Deterministic Policy Engine Guardrails</CardTitle>
        <CardDescription>Hard constraints enforced automatically on all autonomous AI proposals</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200/60 space-y-1">
            <div className="text-xs font-semibold text-slate-500 uppercase">Max Payment Retries</div>
            <div className="text-sm font-bold text-slate-900">3 Attempts per Transaction</div>
            <div className="text-[11px] text-slate-500">Prevents bank rate-limiting & fee spikes</div>
          </div>
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200/60 space-y-1">
            <div className="text-xs font-semibold text-slate-500 uppercase">Max Incentive Discount</div>
            <div className="text-sm font-bold text-slate-900">15% of Invoice Value</div>
            <div className="text-[11px] text-slate-500">Hard limit on recovery concessions</div>
          </div>
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200/60 space-y-1">
            <div className="text-xs font-semibold text-slate-500 uppercase">Precedent Verification</div>
            <div className="text-sm font-bold text-slate-900">Enforce RAG Precedent Verification</div>
            <div className="text-[11px] text-slate-500">Blocks unproven recovery strategies</div>
          </div>
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200/60 space-y-1">
            <div className="text-xs font-semibold text-slate-500 uppercase">Human Escalation Threshold</div>
            <div className="text-sm font-bold text-slate-900">₹50,000 INR</div>
            <div className="text-[11px] text-slate-500">Auto-routes enterprise failures to account team</div>
          </div>
        </div>
      </CardContent>
    </Card>

    <Card className="bg-white border-slate-200/80 shadow-sm">
      <CardHeader>
        <CardTitle>Razorpay Test API Integration Status</CardTitle>
        <CardDescription>Live payment gateway test credentials and webhook receiver</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center justify-between p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-800 text-sm">
          <span className="font-semibold">Razorpay Client Interface:</span>
          <span className="px-2 py-0.5 bg-emerald-200 text-emerald-900 rounded text-xs font-medium">Ready (Sandbox)</span>
        </div>
        <div className="text-xs text-slate-600">
          Webhook Endpoint: <code className="bg-slate-100 px-1 py-0.5 rounded text-slate-800">POST /webhook/razorpay</code> with automated HMAC-SHA256 signature verification.
        </div>
      </CardContent>
    </Card>
  </div>
);

function getRouteFromPathname(): RouteKey {
  const path = window.location.pathname.toLowerCase().replace(/\/$/, '') || '/';
  return PATH_TO_ROUTE[path] || ROUTES.DASHBOARD;
}

export const AppContent: React.FC = () => {
  const [activeTab, setActiveTab] = useState<RouteKey>(getRouteFromPathname);
  const [timeRange, setTimeRange] = useState<string>('all');

  const handleTabChange = useCallback((tab: RouteKey) => {
    setActiveTab(tab);
    const targetPath = ROUTE_TO_PATH[tab] || '/dashboard';
    if (window.location.pathname !== targetPath) {
      window.history.pushState(null, '', targetPath);
    }
  }, []);

  useEffect(() => {
    const onPopState = () => {
      setActiveTab(getRouteFromPathname());
    };
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  return (
    <DashboardLayout
      activeTab={activeTab}
      onTabChange={handleTabChange}
      timeRange={timeRange}
      onTimeRangeChange={setTimeRange}
    >
      {activeTab === ROUTES.DASHBOARD && (
        <DashboardContainer
          timeRange={timeRange}
          onNavigateToCases={() => handleTabChange(ROUTES.CASES)}
        />
      )}
      {activeTab === ROUTES.CASES && <RecoveryCasesContainer />}
      {activeTab === ROUTES.AGENTS && <AgentActivityContainer />}
      {activeTab === ROUTES.SETTINGS && <SettingsView />}
    </DashboardLayout>
  );
};

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  );
}

export default App;
