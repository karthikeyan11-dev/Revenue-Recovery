import React from 'react';
import { Zap } from 'lucide-react';

export interface TimelineItem {
  id?: string;
  agent?: string | null;
  step_name?: string | null;
  decision?: string | null;
  output_summary?: string | null;
  input_summary?: string | null;
  timestamp?: string | null;
}

export interface TimelineViewProps {
  timeline?: TimelineItem[] | null;
}

export const TimelineView: React.FC<TimelineViewProps> = ({ timeline }) => {
  if (!timeline || timeline.length === 0) {
    return (
      <div className="text-xs text-slate-500 italic p-4 text-center">
        No timeline events logged yet.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center space-x-2">
        <Zap className="w-4 h-4 text-brand-400" />
        <span>Multi-Agent Workflow Audit Trail</span>
      </h4>

      <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
        {timeline.map((item, idx) => (
          <div key={item.id || idx} className="relative space-y-1">
            {/* Dot */}
            <div className="absolute -left-6 top-1 w-2.5 h-2.5 rounded-full bg-brand-500 border-2 border-[#09182d]" />

            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white">{item.agent || 'Agent'}</span>
              <span className="text-[11px] font-mono text-slate-500">
                {item.timestamp ? new Date(item.timestamp).toLocaleTimeString() : '—'}
              </span>
            </div>

            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs space-y-1.5">
              <div className="flex items-center justify-between text-slate-400">
                <span className="font-mono text-[11px] text-brand-300">
                  {item.step_name || 'Workflow Step'}
                </span>
                {item.decision && (
                  <span className="text-emerald-400 font-semibold">
                    {item.decision}
                  </span>
                )}
              </div>
              {item.output_summary && (
                <p className="text-slate-300">{item.output_summary}</p>
              )}
              {item.input_summary && (
                <p className="text-[11px] text-slate-500 italic">
                  Input: {item.input_summary}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
