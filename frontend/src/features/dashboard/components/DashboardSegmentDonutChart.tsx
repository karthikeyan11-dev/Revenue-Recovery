import React from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../../components/ui/card';
import { formatCurrency, formatPercent } from '../../../lib/utils';
import { DASHBOARD_CONSTANTS } from '../constants/dashboard.constants';
import type { DashboardSegmentDonutChartProps } from '../types/dashboard.types';

const SEGMENT_COLORS: Record<string, string> = {
  'Bank Declined': '#3b82f6',
  'Authentication Failed': '#10b981',
  'Network Error': '#f59e0b',
  'Insufficient Funds': '#8b5cf6',
  'User Dropoff': '#06b6d4',
  'Expired Card': '#f43f5e',
  'Limit Exceeded': '#64748b',
  'At Risk': '#3b82f6',
  'Low Value': '#10b981',
  'Regular': '#f59e0b',
  'Loyal': '#8b5cf6',
  'High Value': '#06b6d4',
  'Churning': '#f43f5e',
};

const DEFAULT_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4', '#f43f5e', '#64748b'];

export const DashboardSegmentDonutChart: React.FC<DashboardSegmentDonutChartProps> = ({ data }) => {
  return (
    <Card className="bg-white border-slate-200/80 shadow-sm">
      <CardHeader className="pb-2">
        <CardTitle>{DASHBOARD_CONSTANTS.CHARTS.DONUT_TITLE}</CardTitle>
        <CardDescription>{DASHBOARD_CONSTANTS.CHARTS.DONUT_SUBTITLE}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col md:flex-row items-center justify-between pt-2">
          {/* Donut graphic */}
          <div className="h-64 w-full md:w-1/2">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  dataKey="recovered_inr"
                  nameKey="segment"
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={3}
                >
                  {data.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={
                        SEGMENT_COLORS[entry.segment] ||
                        DEFAULT_COLORS[index % DEFAULT_COLORS.length]
                      }
                    />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value: number | string | readonly (number | string)[] | undefined) => {
                    const num = typeof value === 'number' ? value : Number(value || 0);
                    return [formatCurrency(num), 'Recovered'];
                  }}
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    borderRadius: '8px',
                    border: '1px solid #e2e8f0',
                    boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                    fontSize: '12px',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Segment Details Legend */}
          <div className="w-full md:w-1/2 space-y-3 mt-4 md:mt-0 pl-0 md:pl-4">
            {data.map((item, index) => {
              const color =
                SEGMENT_COLORS[item.segment] ||
                DEFAULT_COLORS[index % DEFAULT_COLORS.length];
              return (
                <div key={item.segment} className="flex items-center justify-between text-xs">
                  <div className="flex items-center space-x-2">
                    <span
                      className="w-2.5 h-2.5 rounded-full shrink-0"
                      style={{ backgroundColor: color }}
                    />
                    <span className="font-medium text-slate-700">{item.segment}</span>
                  </div>
                  <div className="flex items-center space-x-3 text-right">
                    <span className="font-semibold text-slate-900">
                      {formatPercent(item.percentage)}
                    </span>
                    <span className="text-slate-500 w-20">
                      {formatCurrency(item.recovered_inr)}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
