import React from 'react';
import { Info, X } from 'lucide-react';
import { Button } from '../../../components/ui/button';
import { formatCurrency, formatPercent } from '../../../lib/utils';
import { DASHBOARD_CONSTANTS } from '../constants/dashboard.constants';
import type { DashboardBaselineBannerProps } from '../types/dashboard.types';

export const DashboardBaselineBanner: React.FC<DashboardBaselineBannerProps> = ({
  metrics,
  onViewDetails,
  onDismiss,
}) => {
  return (
    <div className="flex items-center justify-between bg-blue-50/70 border border-blue-200/80 rounded-xl px-5 py-3.5 shadow-sm">
      <div className="flex items-center space-x-3">
        <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center text-white shrink-0 shadow-sm">
          <Info className="w-4 h-4" />
        </div>
        <div className="text-sm font-medium text-slate-800">
          <span className="font-semibold text-blue-950 mr-1.5">
            {DASHBOARD_CONSTANTS.BANNER.TITLE_PREFIX}
          </span>
          Recovered {formatCurrency(metrics.baseline_recovered_revenue)} (
          {formatPercent(metrics.baseline_recovery_rate)} recovery rate).
        </div>
      </div>

      <div className="flex items-center space-x-2">
        {onViewDetails && (
          <Button
            size="sm"
            variant="outline"
            onClick={onViewDetails}
            className="bg-white border-blue-200 text-blue-700 hover:bg-blue-50 text-xs font-semibold h-8 px-3"
          >
            {DASHBOARD_CONSTANTS.BANNER.VIEW_DETAILS}
          </Button>
        )}
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-blue-100/50 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};
