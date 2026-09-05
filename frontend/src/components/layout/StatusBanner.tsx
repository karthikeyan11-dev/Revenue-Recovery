import React from 'react';
import { Activity, Database, CheckCircle2, AlertCircle } from 'lucide-react';
import { useHealth } from '../../api/hooks/useHealth';

export const StatusBanner: React.FC = () => {
  const { data: health, isPending, isError } = useHealth();

  if (isPending) return null;

  const isHealthy = !isError && health?.status === 'ok';

  return (
    <div
      className={`border-b px-4 py-2 text-xs flex items-center justify-between ${
        isHealthy
          ? 'bg-emerald-950/40 border-emerald-800/40 text-emerald-300'
          : 'bg-rose-950/40 border-rose-800/40 text-rose-300'
      }`}
    >
      <div className="max-w-7xl mx-auto w-full flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1.5 font-medium">
            {isHealthy ? (
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
            ) : (
              <AlertCircle className="h-3.5 w-3.5 text-rose-400" />
            )}
            <span>
              Backend REST API:{' '}
              <strong className="font-semibold">{health?.status?.toUpperCase() || 'OFFLINE'}</strong>
            </span>
          </div>

          <div className="flex items-center space-x-1.5 opacity-80">
            <Database className="h-3.5 w-3.5" />
            <span>
              Database:{' '}
              <strong className="font-semibold">{health?.database || 'disconnected'}</strong>
            </span>
          </div>

          {health?.version && (
            <div className="hidden sm:flex items-center space-x-1.5 opacity-80">
              <Activity className="h-3.5 w-3.5" />
              <span>v{health.version}</span>
            </div>
          )}
        </div>

        <div className="text-[11px] opacity-75 font-mono">
          PostgreSQL 16 + ChromaDB Playbook
        </div>
      </div>
    </div>
  );
};
