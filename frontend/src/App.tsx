import React, { useState } from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { ShieldAlert, Cpu, Layers, Terminal, ArrowUpRight } from 'lucide-react';
import { queryClient } from './lib/queryClient';
import { DashboardLayout } from './components/layout/DashboardLayout';
import { HealthStatusCard } from './components/HealthStatusCard';
import { DashboardContainer } from './features/dashboard';
import { RecoveryCasesContainer } from './features/recovery-cases';
import { AgentActivityContainer } from './features/agent-activity';
import { ROUTES } from './constants/routes';
import type { RouteKey } from './constants/routes';

export const AppContent: React.FC = () => {
  const [activeTab, setActiveTab] = useState<RouteKey>(ROUTES.OVERVIEW);

  return (
    <DashboardLayout activeTab={activeTab} onTabChange={setActiveTab}>
      {activeTab === ROUTES.OVERVIEW && (
        <div className="space-y-8 animate-in fade-in duration-200">
          {/* Mission & Key Architectural Principle */}
          <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#0c2340] via-[#091e38] to-[#07162c] p-8 border border-slate-700/60 shadow-2xl">
            <div className="relative z-10 max-w-3xl space-y-3">
              <div className="inline-flex items-center space-x-2 px-2.5 py-1 rounded-full bg-brand-500/10 text-brand-400 text-xs font-mono border border-brand-500/30">
                <ShieldAlert className="w-3.5 h-3.5" />
                <span>Core Architectural Principle</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                The LLM Proposes Decisions. <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-400 to-razorpay-accent">
                  A Deterministic Policy Engine Decides.
                </span>
              </h1>
              <p className="text-slate-300 text-sm leading-relaxed">
                An autonomous AI system detecting revenue at risk from failed payments & abandoned
                checkouts, evaluating customer context, selecting bounded recovery actions, and
                empirically measuring recovered ₹ against a naive baseline.
              </p>
            </div>
          </div>

          {/* Health Status Probe Card */}
          <HealthStatusCard />

          {/* Architecture Node Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-5 rounded-xl bg-[#0c2340]/60 border border-slate-800 hover:border-slate-700 transition-colors">
              <div className="flex items-center justify-between text-brand-400 mb-3">
                <Cpu className="w-5 h-5" />
                <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
                  Node 01
                </span>
              </div>
              <h4 className="text-sm font-semibold text-white mb-1">Revenue Detective</h4>
              <p className="text-xs text-slate-400">
                Rules + LLM reasoning for leak identification and recoverability scoring.
              </p>
            </div>

            <div className="p-5 rounded-xl bg-[#0c2340]/60 border border-slate-800 hover:border-slate-700 transition-colors">
              <div className="flex items-center justify-between text-brand-400 mb-3">
                <Layers className="w-5 h-5" />
                <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
                  Node 02
                </span>
              </div>
              <h4 className="text-sm font-semibold text-white mb-1">Customer Intelligence</h4>
              <p className="text-xs text-slate-400">
                Customer profiling, churn risk evaluation, and channel affinity calculation.
              </p>
            </div>

            <div className="p-5 rounded-xl bg-[#0c2340]/60 border border-slate-800 hover:border-slate-700 transition-colors">
              <div className="flex items-center justify-between text-brand-400 mb-3">
                <Terminal className="w-5 h-5" />
                <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
                  Node 03
                </span>
              </div>
              <h4 className="text-sm font-semibold text-white mb-1">Recovery Strategist</h4>
              <p className="text-xs text-slate-400">
                Pydantic structured action proposals (Retry, WhatsApp, Discount, Escalate).
              </p>
            </div>

            <div className="p-5 rounded-xl bg-[#0c2340]/60 border border-slate-800 hover:border-slate-700 transition-colors">
              <div className="flex items-center justify-between text-brand-400 mb-3">
                <ArrowUpRight className="w-5 h-5" />
                <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
                  Node 04
                </span>
              </div>
              <h4 className="text-sm font-semibold text-white mb-1">Recovery Analyst</h4>
              <p className="text-xs text-slate-400">
                Empirical ROI computation & baseline vs AI comparative analytics.
              </p>
            </div>
          </div>
        </div>
      )}

      {activeTab === ROUTES.DASHBOARD && <DashboardContainer />}
      {activeTab === ROUTES.CASES && <RecoveryCasesContainer />}
      {activeTab === ROUTES.AGENTS && <AgentActivityContainer />}
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
