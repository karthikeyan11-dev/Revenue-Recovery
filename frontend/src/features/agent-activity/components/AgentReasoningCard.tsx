import React from 'react';
import { Eye, Brain, Crosshair, ShieldCheck, Zap, XCircle, AlertTriangle, CheckCircle2 } from 'lucide-react';
import type { AgentActivityItem } from '../../../types/agent';
import { ConfidenceGauge } from './ConfidenceGauge';

export interface AgentReasoningCardProps {
  activity: AgentActivityItem;
}

export const AgentReasoningCard: React.FC<AgentReasoningCardProps> = ({ activity }) => {
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
    <div className="p-5 rounded-2xl bg-[#0c2340]/90 border border-slate-800 hover:border-slate-700 transition shadow-lg space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div className="flex items-center space-x-3">
          {getAgentBadge(activity.agent)}
          <span className="font-mono text-xs text-brand-300 font-bold">
            Step: {activity.step_name}
          </span>
          {activity.case_id && (
            <span className="text-[11px] font-mono text-slate-500 hidden md:inline">
              Case: {activity.case_id.substring(0, 12)}
            </span>
          )}
        </div>
        <div className="flex items-center space-x-2">
          {getDecisionBadge(activity.decision)}
          <span className="text-[11px] font-mono text-slate-500">
            {new Date(activity.timestamp).toLocaleTimeString()}
          </span>
        </div>
      </div>

      {/* Output / Reasoning Content */}
      <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800/80 text-xs space-y-2">
        <div className="text-slate-200 font-sans leading-relaxed">
          {activity.output_summary}
        </div>
        {activity.input_summary && (
          <div className="text-[11px] text-slate-400 border-t border-slate-800/80 pt-2 flex items-start space-x-1 font-mono">
            <span className="text-slate-500 shrink-0">Telemetry Input:</span>
            <span className="truncate">{activity.input_summary}</span>
          </div>
        )}
      </div>

      {/* Laplace Empirical Confidence Telemetry Gauge */}
      {activity.confidence !== null && activity.confidence !== undefined && (
        <ConfidenceGauge
          confidence={activity.confidence}
          llmStatedConfidence={activity.llm_stated_confidence}
          sampleSize={activity.precedent_sample_size}
        />
      )}
    </div>
  );
};
