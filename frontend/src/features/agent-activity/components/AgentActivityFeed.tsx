import React from 'react';
import { Bot, Clock } from 'lucide-react';
import { Badge } from '../../../components/ui/badge';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { formatDate, formatPercent } from '../../../lib/utils';
import { AGENT_ACTIVITY_CONSTANTS } from '../constants/agent-activity.constants';
import type { AgentActivityFeedProps } from '../types/agent-activity.types';

export const AgentActivityFeed: React.FC<AgentActivityFeedProps> = ({
  activities,
  totalEvents,
}) => {
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'Approved':
        return <Badge variant="success">Approved</Badge>;
      case 'Completed':
        return <Badge variant="info">Completed</Badge>;
      case 'Escalated':
        return <Badge variant="destructive">Escalated</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  return (
    <Card className="bg-white border-slate-200/80 shadow-sm">
      <CardHeader className="p-4 border-b border-slate-100 flex flex-row items-center justify-between">
        <div className="flex items-center space-x-2">
          <CardTitle className="text-sm font-bold text-slate-900">
            {AGENT_ACTIVITY_CONSTANTS.FEED_TITLE}
          </CardTitle>
          <Badge variant="secondary" className="text-[11px] bg-slate-100 text-slate-600">
            {totalEvents} {AGENT_ACTIVITY_CONSTANTS.EVENTS_RECORDED}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="p-4 space-y-3">
        {activities.length === 0 ? (
          <div className="text-center py-12 text-xs text-slate-500">
            {AGENT_ACTIVITY_CONSTANTS.EMPTY_STATE}
          </div>
        ) : (
          activities.map((item) => (
            <div
              key={item.id}
              className="p-4 rounded-xl border border-slate-200/70 bg-slate-50/50 hover:bg-white hover:border-slate-300 transition-all space-y-2.5 shadow-sm"
            >
              {/* Event Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2.5">
                  <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center text-white text-xs font-bold shadow-sm">
                    <Bot className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-xs font-bold text-slate-900 mr-2">{item.agent}</span>
                    <Badge variant="outline" className="text-[10px] bg-white border-slate-200 text-slate-700">
                      {item.action_name}
                    </Badge>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  {getStatusBadge(item.status)}
                  <span className="text-[11px] text-slate-400 font-medium">
                    {formatDate(item.timestamp)}
                  </span>
                </div>
              </div>

              {/* Case ID and Decision */}
              <div className="flex flex-wrap items-center gap-2 text-xs">
                <span className="font-mono text-[11px] bg-white px-2 py-0.5 rounded border border-slate-200 font-semibold text-slate-700">
                  {item.case_id}
                </span>
                <span className="text-slate-600 font-medium">
                  {AGENT_ACTIVITY_CONSTANTS.DECISION_LABEL}{' '}
                  <span className="font-semibold text-slate-900">
                    {item.decision || AGENT_ACTIVITY_CONSTANTS.PROCESSED_FALLBACK}
                  </span>
                </span>
              </div>

              {/* Output Summary */}
              {item.output_summary && (
                <div className="p-2.5 rounded-lg bg-white border border-slate-200/60 text-xs text-slate-700 font-mono leading-relaxed">
                  {item.output_summary}
                </div>
              )}

              {/* Telemetry Bar */}
              <div className="flex flex-wrap items-center justify-between pt-1 text-[11px] text-slate-500 border-t border-slate-200/40">
                <div className="flex items-center space-x-4">
                  <span>
                    {AGENT_ACTIVITY_CONSTANTS.EMPIRICAL_CONFIDENCE_LABEL}{' '}
                    <span className="font-bold text-emerald-600">
                      {formatPercent((item.empirical_confidence ?? item.confidence) * 100)}
                    </span>
                  </span>
                  <span>
                    {AGENT_ACTIVITY_CONSTANTS.PRECEDENTS_LABEL}{' '}
                    <span className="font-semibold text-slate-700">
                      {item.precedent_sample_size ?? 5} cases
                    </span>
                  </span>
                </div>

                <div className="flex items-center space-x-1 text-slate-400 font-mono">
                  <Clock className="w-3 h-3" />
                  <span>{item.duration_seconds}s {AGENT_ACTIVITY_CONSTANTS.LATENCY_LABEL}</span>
                </div>
              </div>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
};
