import React, { useState } from 'react';
import {
  Activity,
  Zap,
  RefreshCw,
  Clock,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Eye,
  Brain,
  Crosshair,
  ShieldCheck,
  Database,
  Gauge,
  Sparkles,
} from 'lucide-react';
import { useAgentActivityQuery } from '../api/hooks/useAgentActivity';

export const AgentActivity: React.FC = () => {
  const [selectedAgent, setSelectedAgent] = useState<string>('ALL');
  const [filterDecision, setFilterDecision] = useState<string>('ALL');

  const { data: activityData, isLoading, isFetching, refetch } = useAgentActivityQuery(60);

  const activities = activityData?.activities || [];

  const filteredActivities = activities.filter((act) => {
    if (selectedAgent !== 'ALL' && act.agent !== selectedAgent) return false;
    if (filterDecision === 'POLICY_REJECTIONS' && act.decision !== 'REJECTED') return false;
    if (filterDecision === 'POLICY_ESCALATIONS' && act.decision !== 'ESCALATED') return false;
    if (filterDecision === 'RECOVERIES' && act.decision !== 'RECOVERED') return false;
    return true;
  });

  const getAgentIcon = (agent: string) => {
    switch (agent) {
      case 'Revenue Detective':
        return <Eye className="w-4 h-4 text-cyan-400" />;
      case 'Customer Intelligence':
        return <Brain className="w-4 h-4 text-purple-400" />;
      case 'Recovery Strategist':
        return <Crosshair className="w-4 h-4 text-amber-400" />;
      case 'Policy Engine':
        return <ShieldCheck className="w-4 h-4 text-rose-400" />;
      default:
        return <Zap className="w-4 h-4 text-emerald-400" />;
    }
  };

  const getAgentBadge = (agent: string) => {
    const badges: Record<string, string> = {
      'Revenue Detective': 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30',
      'Customer Intelligence': 'bg-purple-500/10 text-purple-300 border-purple-500/30',
      'Recovery Strategist': 'bg-amber-500/10 text-amber-300 border-amber-500/30',
      'Policy Engine': 'bg-rose-500/10 text-rose-300 border-rose-500/30',
      'Action Executor': 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30',
    };
    return (
      <span
        className={`px-2.5 py-1 rounded-full text-xs font-semibold flex items-center space-x-1.5 border ${
          badges[agent] || 'bg-slate-800 text-slate-300 border-slate-700'
        }`}
      >
        {getAgentIcon(agent)}
        <span>{agent}</span>
      </span>
    );
  };

  const getDecisionBadge = (decision?: string | null) => {
    const dec = decision || 'UNKNOWN';
    if (dec === 'REJECTED') {
      return (
        <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-500/20 text-rose-400 border border-rose-500/40 flex items-center space-x-1">
          <XCircle className="w-3.5 h-3.5" />
          <span>POLICY REJECTED</span>
        </span>
      );
    }
    if (dec === 'ESCALATED') {
      return (
        <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-500/20 text-amber-400 border border-amber-500/40 flex items-center space-x-1">
          <AlertTriangle className="w-3.5 h-3.5" />
          <span>HUMAN ESCALATION</span>
        </span>
      );
    }
    if (dec === 'RECOVERED' || dec === 'APPROVED') {
      return (
        <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center space-x-1">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>{dec}</span>
        </span>
      );
    }
    return (
      <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-800 text-slate-300 border border-slate-700">
        {dec}
      </span>
    );
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header Bar */}
      <div className="p-6 rounded-2xl bg-[#0c2340]/90 border border-slate-800 backdrop-blur shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <span className="flex h-3 w-3 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
            </span>
            <h2 className="text-xl font-bold text-white tracking-tight">
              Live Agent Reasoning & Decision Stream
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time audit telemetry capturing empirical vs LLM confidence metrics, RAG precedent
            counts, and deterministic policy outcomes.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="text-xs text-slate-400 font-mono flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800">
            <Clock className="w-3.5 h-3.5 text-brand-400" />
            <span>Auto-polling (5s)</span>
          </div>

          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center space-x-1.5 border border-slate-700 transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Filter Chips Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-4 rounded-xl bg-[#0c2340]/60 border border-slate-800">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-slate-400 mr-1">Agent:</span>
          {[
            'ALL',
            'Revenue Detective',
            'Customer Intelligence',
            'Recovery Strategist',
            'Policy Engine',
            'Action Executor',
          ].map((ag) => (
            <button
              key={ag}
              onClick={() => setSelectedAgent(ag)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition ${
                selectedAgent === ag
                  ? 'bg-brand-600 text-white font-semibold shadow'
                  : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {ag === 'ALL' ? 'All Agents' : ag}
            </button>
          ))}
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold text-slate-400">Filter:</span>
          <select
            value={filterDecision}
            onChange={(e) => setFilterDecision(e.target.value)}
            className="px-3 py-1 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-300 focus:outline-none"
          >
            <option value="ALL">All Decisions</option>
            <option value="POLICY_REJECTIONS">Policy Rejections ❌</option>
            <option value="POLICY_ESCALATIONS">Escalations ⚠️</option>
            <option value="RECOVERIES">Recovered Funds 💰</option>
          </select>
        </div>
      </div>

      {/* Live Activity Feed */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="py-20 text-center text-slate-500">
            <Activity className="w-8 h-8 animate-spin mx-auto mb-2 text-brand-400" />
            Loading live decision telemetry...
          </div>
        ) : filteredActivities.length === 0 ? (
          <div className="py-20 text-center text-slate-500 rounded-2xl bg-[#0c2340]/40 border border-slate-800">
            No agent activity found. Execute an AI Orchestrator simulation run to watch live
            decisions.
          </div>
        ) : (
          filteredActivities.map((act) => {
            const isRejection = act.decision === 'REJECTED';
            const isEscalation = act.decision === 'ESCALATED';
            const isAiAgent = [
              'Revenue Detective',
              'Customer Intelligence',
              'Recovery Strategist',
            ].includes(act.agent);

            const empiricalConf =
              act.empirical_confidence !== null && act.empirical_confidence !== undefined
                ? act.empirical_confidence
                : act.confidence;

            const llmConf = act.llm_stated_confidence;
            const precedentCount = act.precedent_sample_size || 0;

            return (
              <div
                key={act.id}
                className={`p-5 rounded-2xl border transition-all shadow-xl ${
                  isRejection
                    ? 'bg-rose-950/20 border-rose-500/40 hover:border-rose-500/70'
                    : isEscalation
                      ? 'bg-amber-950/20 border-amber-500/40 hover:border-amber-500/70'
                      : 'bg-[#0c2340]/80 border-slate-800/90 hover:border-slate-700'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-800/80">
                  <div className="flex items-center space-x-3">
                    {getAgentBadge(act.agent)}
                    <span className="font-mono text-xs text-brand-400 font-bold">
                      Case: {act.case_id}
                    </span>
                    <span className="text-xs text-slate-400 font-mono">[{act.step_name}]</span>
                  </div>

                  <div className="flex items-center space-x-3">
                    <span className="text-[11px] font-mono text-slate-500">
                      {new Date(act.timestamp).toLocaleTimeString()}
                    </span>
                    {getDecisionBadge(act.decision)}
                  </div>
                </div>

                <div className="mt-3 space-y-2 text-xs">
                  {/* Dual Confidence & Precedents Bar */}
                  {isAiAgent && (
                    <div className="flex flex-wrap items-center gap-2 p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/90">
                      {/* Empirical Confidence */}
                      <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                        <Gauge className="w-3.5 h-3.5 text-emerald-400" />
                        <span className="text-[11px] text-slate-400 font-medium">
                          Empirical Confidence:
                        </span>
                        <span className="font-mono font-bold text-emerald-400 text-xs">
                          {(empiricalConf * 100).toFixed(1)}%
                        </span>
                      </div>

                      {/* LLM Stated Confidence */}
                      {llmConf !== null && llmConf !== undefined && (
                        <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-purple-500/10 border border-purple-500/20">
                          <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                          <span className="text-[11px] text-slate-400 font-medium">
                            LLM Stated Confidence:
                          </span>
                          <span className="font-mono font-bold text-purple-300 text-xs">
                            {(llmConf * 100).toFixed(0)}%
                          </span>
                        </div>
                      )}

                      {/* Strategist Specific: Precedent Count */}
                      {act.agent === 'Recovery Strategist' && (
                        <div
                          className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-lg border ${
                            precedentCount >= 3
                              ? 'bg-cyan-500/10 border-cyan-500/20 text-cyan-300'
                              : 'bg-amber-500/10 border-amber-500/30 text-amber-300'
                          }`}
                        >
                          <Database className="w-3.5 h-3.5" />
                          <span className="text-[11px] font-medium">Retrieved Precedents:</span>
                          <span className="font-mono font-bold text-xs">n={precedentCount}</span>
                          {precedentCount < 3 && (
                            <span className="text-[10px] text-amber-400 font-semibold">
                              (Insufficient &lt; 3)
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  )}

                  <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-slate-200 font-sans leading-relaxed">
                    <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
                      Reasoning & Decision Output
                    </div>
                    <p className="text-sm font-medium text-slate-100">{act.output_summary}</p>
                  </div>

                  <div className="text-[11px] text-slate-400 font-mono flex items-center space-x-2 pl-1">
                    <span className="text-slate-500">Input Context:</span>
                    <span>{act.input_summary}</span>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
