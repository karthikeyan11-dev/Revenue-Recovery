import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../../components/ui/card';
import { formatCurrency } from '../../../lib/utils';
import { DASHBOARD_CONSTANTS } from '../constants/dashboard.constants';
import type { DashboardSegmentComparisonChartProps } from '../types/dashboard.types';

export const DashboardSegmentComparisonChart: React.FC<DashboardSegmentComparisonChartProps> = ({
  data,
}) => {
  const chartData = data.map((item) => ({
    segment: item.segment,
    'At Risk': item.total_at_risk_inr,
    'Baseline (Retry Once)': item.baseline_recovered_inr,
    'AI Orchestrator': item.ai_recovered_inr,
  }));

  return (
    <Card className="bg-white border-slate-200/80 shadow-sm">
      <CardHeader className="pb-2">
        <CardTitle>{DASHBOARD_CONSTANTS.CHARTS.COMPARISON_TITLE}</CardTitle>
        <CardDescription>{DASHBOARD_CONSTANTS.CHARTS.COMPARISON_SUBTITLE}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-88 w-full pt-4">
          <ResponsiveContainer width="100%" height={340}>
            <BarChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 15 }} barGap={4}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
              <XAxis
                dataKey="segment"
                interval={0}
                angle={0}
                textAnchor="middle"
                height={35}
                dy={6}
                tick={{ fill: '#475569', fontSize: 12, fontWeight: 500 }}
                tickLine={false}
                axisLine={{ stroke: '#cbd5e1' }}
              />
              <YAxis
                tickFormatter={(val) => `₹${(val / 1000).toFixed(0)}k`}
                tick={{ fill: '#64748b', fontSize: 12 }}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip
                formatter={(value: unknown, name: unknown) => [
                  formatCurrency(Number(value) || 0),
                  String(name ?? ''),
                ]}
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderRadius: '8px',
                  border: '1px solid #e2e8f0',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                  fontSize: '12px',
                }}
              />
              <Legend
                wrapperStyle={{ paddingTop: '8px', fontSize: '12px' }}
                iconType="circle"
              />
              <Bar dataKey="At Risk" fill="#94a3b8" radius={[4, 4, 0, 0]} maxBarSize={32} />
              <Bar
                dataKey="Baseline (Retry Once)"
                fill="#38bdf8"
                radius={[4, 4, 0, 0]}
                maxBarSize={32}
              />
              <Bar
                dataKey="AI Orchestrator"
                fill="#2563eb"
                radius={[4, 4, 0, 0]}
                maxBarSize={32}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center text-[11px] text-slate-500">
          <p>
            <strong className="text-slate-700 font-semibold">Policy Guardrail Note:</strong> In categories with whale transactions (&gt;₹25,000), revenue is safely held in the <span className="font-semibold text-indigo-600">Human Escalation Queue</span> to prevent chargeback penalties, while baseline blind retries risk merchant fees.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};
