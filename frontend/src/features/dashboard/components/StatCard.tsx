import React from 'react';

export interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  iconBg?: string;
  trend?: string;
  trendColor?: string;
  badge?: string;
  badgeColor?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  iconBg = 'bg-brand-500/10 text-brand-400',
  trend,
  trendColor = 'text-emerald-400',
  badge,
  badgeColor = 'bg-slate-800 text-slate-300',
}) => {
  return (
    <div className="bg-[#0c2340]/60 border border-slate-800/80 rounded-xl p-5 backdrop-blur-sm shadow-md hover:border-slate-700/80 transition-all">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
          {title}
        </span>
        <div className={`h-8 w-8 rounded-lg flex items-center justify-center ${iconBg}`}>
          {icon}
        </div>
      </div>
      <div className="mt-3">
        <div className="text-2xl font-bold text-white tracking-tight">{value}</div>
        {(subtitle || trend || badge) && (
          <div className="mt-1.5 flex items-center gap-2 text-xs">
            {trend && <span className={`font-semibold ${trendColor}`}>{trend}</span>}
            {subtitle && <span className="text-slate-400">{subtitle}</span>}
            {badge && (
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium border border-current/20 ${badgeColor}`}>
                {badge}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
