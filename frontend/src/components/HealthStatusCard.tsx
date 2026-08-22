import React from 'react';
import { Activity, Shield, Database, CheckCircle2, AlertTriangle, RefreshCw } from 'lucide-react';
import { useHealthQuery } from '../api';

export const HealthStatusCard: React.FC = () => {
  const { data, error, isLoading, isFetching, refetch } = useHealthQuery();


  return (
    <div className="bg-[#0c2340]/90 backdrop-blur-md border border-slate-700/60 rounded-xl p-6 shadow-xl">
      <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-4">
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
          <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? 'animate-spin' : ''}`} />
          <span>{isFetching ? 'Checking...' : 'Check Status'}</span>
        </button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-8 text-slate-400">
          <RefreshCw className="w-6 h-6 animate-spin mr-3 text-brand-400" />
          <span>Verifying orchestrator backend connection...</span>
        </div>
      ) : error ? (
        <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 flex items-start space-x-3">
          <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5 text-rose-400" />
          <div>
            <div className="font-medium">Backend Unreachable</div>
            <div className="text-xs text-rose-400 mt-1">
              {(error as Error)?.message || 'Make sure the FastAPI backend is running on port 8000.'}
            </div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* API Status */}
          <div className="p-4 rounded-lg bg-[#07162c] border border-slate-800 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Shield className="w-5 h-5 text-brand-400" />
              <div>
                <div className="text-xs text-slate-400 font-medium">FastAPI Engine</div>
                <div className="text-sm font-semibold text-white">v{data?.version}</div>
              </div>
            </div>
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1.5 animate-pulse"></span>
              Online
            </span>
          </div>

          {/* Database Status */}
          <div className="p-4 rounded-lg bg-[#07162c] border border-slate-800 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Database className="w-5 h-5 text-brand-400" />
              <div>
                <div className="text-xs text-slate-400 font-medium">PostgreSQL Link</div>
                <div className="text-sm font-semibold text-white">
                  {data?.database === 'connected' ? 'Connected' : 'Unavailable'}
                </div>
              </div>
            </div>
            <span
              className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                data?.database === 'connected'
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                  : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
              }`}
            >
              <span
                className={`w-1.5 h-1.5 rounded-full mr-1.5 ${
                  data?.database === 'connected' ? 'bg-emerald-400' : 'bg-amber-400'
                }`}
              ></span>
              {data?.database === 'connected' ? 'Ready' : 'Degraded'}
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
      )}
    </div>
  );
};
