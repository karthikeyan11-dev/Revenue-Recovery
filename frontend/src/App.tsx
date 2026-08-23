import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ShieldAlert, Zap, Layers, Cpu, Terminal, ArrowUpRight } from 'lucide-react';
import { HealthStatusCard } from './components/HealthStatusCard';
import { Dashboard } from './pages/Dashboard';
import { RecoveryCases } from './pages/RecoveryCases';
import { AgentActivity } from './pages/AgentActivity';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 5000,
    },
  },
});

export const AppContent: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'dashboard' | 'cases' | 'agents'>(
    'overview'
  );

  return (
    <div className="min-h-screen bg-[#07162c] text-slate-100 flex flex-col">
      {/* Top Banner */}
      <header className="border-b border-slate-800 bg-[#0c2340]/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="h-9 w-9 rounded-lg bg-gradient-to-tr from-brand-600 to-razorpay-accent flex items-center justify-center shadow-lg shadow-brand-500/20">
              <Zap className="h-5 w-5 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-white tracking-tight text-lg">
                  AI Revenue Recovery
                </span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-brand-500/20 text-brand-300 font-medium border border-brand-500/30">
                  Track 03
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-mono">
                Razorpay AI Buildathon — Autonomous Policy-Governed Orchestrator
              </p>
            </div>
          </div>

          <nav className="flex items-center space-x-1 sm:space-x-2">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === 'overview'
                  ? 'bg-brand-600 text-white shadow-md shadow-brand-500/25'
                  : 'text-slate-300 hover:bg-slate-800'
              }`}
              id="nav-tab-overview"
            >
              System Health
            </button>
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === 'dashboard'
                  ? 'bg-brand-600 text-white shadow-md shadow-brand-500/25'
                  : 'text-slate-300 hover:bg-slate-800'
              }`}
              id="nav-tab-dashboard"
            >
              Dashboard
            </button>
            <button
              onClick={() => setActiveTab('cases')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === 'cases'
                  ? 'bg-brand-600 text-white shadow-md shadow-brand-500/25'
                  : 'text-slate-300 hover:bg-slate-800'
              }`}
              id="nav-tab-cases"
            >
              Recovery Cases
            </button>
            <button
              onClick={() => setActiveTab('agents')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === 'agents'
                  ? 'bg-brand-600 text-white shadow-md shadow-brand-500/25'
                  : 'text-slate-300 hover:bg-slate-800'
              }`}
              id="nav-tab-agents"
            >
              Agent Activity
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {activeTab === 'overview' && (
          <div className="space-y-8 animate-fadeIn">
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

        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'cases' && <RecoveryCases />}
        {activeTab === 'agents' && <AgentActivity />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-[#07162c] py-4">
        <div className="max-w-7xl mx-auto px-4 text-center text-xs text-slate-400">
          AI Revenue Recovery Orchestrator • Razorpay Buildathon 2026 • Production Scaffolding Ready
        </div>
      </footer>
    </div>
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
