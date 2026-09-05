import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts';

export interface RecoveryComparisonChartProps {
  data: Array<{
    segment: string;
    total_at_risk_inr: number;
    baseline_recovered_inr: number;
    ai_recovered_inr: number;
  }>;
}

export const RecoveryComparisonChart: React.FC<RecoveryComparisonChartProps> = ({ data }) => {
  const chartData = (data || []).map((item) => ({
    name: item.segment,
    'At Risk (₹)': item.total_at_risk_inr,
    'Baseline Recovered (₹)': item.baseline_recovered_inr,
    'AI Recovered (₹)': item.ai_recovered_inr,
  }));

  if (chartData.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-500 text-sm italic">
        No cohort data generated yet. Click "Generate Synthetic Cohort" above.
      </div>
    );
  }

  return (
    <div className="h-80 w-full pt-4">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 10, right: 30, left: 20, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis dataKey="name" stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} />
          <YAxis
            stroke="#64748b"
            tick={{ fill: '#94a3b8', fontSize: 11 }}
            tickFormatter={(val) => `₹${(val / 1000).toFixed(0)}k`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#0c2340',
              borderColor: '#1e293b',
              borderRadius: '0.75rem',
              color: '#f8fafc',
              fontSize: '12px',
            }}
            formatter={(value: unknown) => [
              `₹${Number(value ?? 0).toLocaleString('en-IN')}`,
              '',
            ]}
          />
          <Legend wrapperStyle={{ paddingTop: '10px', fontSize: '12px' }} />
          <Bar dataKey="At Risk (₹)" fill="#e11d48" radius={[4, 4, 0, 0]} opacity={0.7} />
          <Bar dataKey="Baseline Recovered (₹)" fill="#64748b" radius={[4, 4, 0, 0]} opacity={0.8} />
          <Bar dataKey="AI Recovered (₹)" fill="#10b981" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
