import React from 'react';
import {
  Activity,
  Shield,
  Database,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  XCircle,
} from 'lucide-react';
import { useHealthQuery } from '../api';

export const HealthStatusCard: React.FC = () => {
  const { data, error, isLoading, isFetching, refetch } = useHealthQuery();

  const isDbConnected = data?.database === 'connected';

  return (
    <div className="bg-[#0c2340]/90 backdrop-blur-md border border-slate-700/60 rounded-xl p-6 shadow-xl space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-brand-500/10 rounded-lg border border-brand-500/30 text-brand-400">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">System Architecture & Connectivity</h3>
            <p className="text-xs text-slate-400">Backend API, Database Link & Service Probes</p>
          </div>
        </div>

        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="inline-flex items-center space-x-2 text-xs font-medium px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 transition-colors disabled:opacity-50"
          id="btn-refresh-health"
        >
          {isFetching ? (
            <img
              src="/revenue-recovery-logo-alone.png"
              alt="Loading"
              className="w-3.5 h-3.5 animate-logo-pulse object-contain inline-block"
            />
          ) : (
            <RefreshCw className="w-3.5 h-3.5" />
          )}
          <span>{isFetching ? 'Checking...' : 'Check Status'}</span>
        </button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-8 text-slate-400">
          <img
            src="/revenue-recovery-logo-alone.png"
            alt="Loading"
            className="w-8 h-8 object-contain animate-logo-pulse mr-3"
          />
          <span>Verifying orchestrator backend connection...</span>
        </div>
      ) : error ? (
        <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 flex items-start space-x-3">
          <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5 text-rose-400" />
          <div>
            <div className="font-medium">Backend API Offline</div>
            <div className="text-xs text-rose-400 mt-1">
              FastAPI backend is not running on port 8000. Start it with:{' '}
              <code className="bg-black/40 px-1.5 py-0.5 rounded font-mono">
                cd backend && uvicorn app.main:app --reload
              </code>
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Component Status Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* FastAPI Engine Status */}
            <div className="p-4 rounded-lg bg-[#07162c] border border-slate-800 flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Shield className="w-5 h-5 text-brand-400" />
                <div>
                  <div className="text-xs text-slate-400 font-medium">FastAPI Engine</div>
                  <div className="text-sm font-semibold text-white">
                    v{data?.version || '0.1.0'}
                  </div>
                </div>
              </div>
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1.5 animate-pulse"></span>
                Online
              </span>
            </div>

            {/* PostgreSQL Link Status */}
            <div
              className={`p-4 rounded-lg border flex items-center justify-between transition-all ${
                isDbConnected
                  ? 'bg-[#07162c] border-slate-800'
                  : 'bg-rose-950/20 border-rose-500/40'
              }`}
            >
              <div className="flex items-center space-x-3">
                <Database
                  className={`w-5 h-5 ${isDbConnected ? 'text-brand-400' : 'text-rose-400'}`}
                />
                <div>
                  <div className="text-xs text-slate-400 font-medium">PostgreSQL Link</div>
                  <div
                    className={`text-sm font-semibold ${
                      isDbConnected ? 'text-white' : 'text-rose-300'
                    }`}
                  >
                    {isDbConnected ? 'Connected' : 'Unavailable'}
                  </div>
                </div>
              </div>
              <span
                className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                  isDbConnected
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                    : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                }`}
              >
                <span
                  className={`w-1.5 h-1.5 rounded-full mr-1.5 ${
                    isDbConnected ? 'bg-emerald-400' : 'bg-rose-400'
                  }`}
                ></span>
                {isDbConnected ? 'Ready' : 'Not Ready'}
              </span>
            </div>

            {/* Policy Enforcer Status */}
            <div className="p-4 rounded-lg bg-[#07162c] border border-slate-800 flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <CheckCircle2 className="w-5 h-5 text-brand-400" />
                <div>
                  <div className="text-xs text-slate-400 font-medium">Policy Gatekeeper</div>
                  <div className="text-sm font-semibold text-white">Deterministic Guard</div>
                </div>
              </div>
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-brand-500/10 text-brand-400 border border-brand-500/30">
                Active
              </span>
            </div>
          </div>

          {/* Database Degraded Notification Banner */}
          {!isDbConnected && (
            <div className="p-3.5 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 flex items-start space-x-3 animate-fadeIn">
              <XCircle className="w-4 h-4 flex-shrink-0 mt-0.5 text-rose-400" />
              <div className="text-xs space-y-1">
                <span className="font-semibold text-rose-200">
                  Database is stopped or unreachable
                </span>
                <p className="text-rose-400 leading-relaxed">
                  The FastAPI engine is active, but PostgreSQL is offline. Run{' '}
                  <code className="bg-black/50 px-1.5 py-0.5 rounded font-mono text-rose-200">
                    docker start revenue_recovery_db
                  </code>{' '}
                  or{' '}
                  <code className="bg-black/50 px-1.5 py-0.5 rounded font-mono text-rose-200">
                    make up
                  </code>{' '}
                  to resume database operations.
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
