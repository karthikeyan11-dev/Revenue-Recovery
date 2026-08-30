import React from 'react';
import { Search, RotateCcw } from 'lucide-react';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../../components/ui/select';
import { RECOVERY_CASES_CONSTANTS } from '../constants/recovery-cases.constants';
import type { RecoveryCasesFiltersProps } from '../types/recovery-cases.types';

export const RecoveryCasesFilters: React.FC<RecoveryCasesFiltersProps> = ({
  filters,
  onFilterChange,
  onResetFilters,
}) => {
  return (
    <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
      {/* Search Input */}
      <div className="relative w-full md:w-80">
        <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
        <Input
          type="text"
          placeholder={RECOVERY_CASES_CONSTANTS.SEARCH_PLACEHOLDER}
          value={filters.search}
          onChange={(e) => onFilterChange('search', e.target.value)}
          className="pl-9 text-xs h-9 bg-slate-50 border-slate-200"
        />
      </div>

      {/* Dropdown Filters */}
      <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
        {/* Status Dropdown */}
        <div className="w-36">
          <Select value={filters.status} onValueChange={(val) => onFilterChange('status', val)}>
            <SelectTrigger className="h-9 text-xs">
              <SelectValue placeholder={RECOVERY_CASES_CONSTANTS.FILTER_LABELS.STATUS} />
            </SelectTrigger>
            <SelectContent>
              {RECOVERY_CASES_CONSTANTS.STATUS_OPTIONS.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Failure Reason Dropdown */}
        <div className="w-44">
          <Select value={filters.reason} onValueChange={(val) => onFilterChange('reason', val)}>
            <SelectTrigger className="h-9 text-xs">
              <SelectValue placeholder={RECOVERY_CASES_CONSTANTS.FILTER_LABELS.REASON} />
            </SelectTrigger>
            <SelectContent>
              {RECOVERY_CASES_CONSTANTS.REASON_OPTIONS.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Priority Dropdown */}
        <div className="w-36">
          <Select value={filters.priority} onValueChange={(val) => onFilterChange('priority', val)}>
            <SelectTrigger className="h-9 text-xs">
              <SelectValue placeholder={RECOVERY_CASES_CONSTANTS.FILTER_LABELS.PRIORITY} />
            </SelectTrigger>
            <SelectContent>
              {RECOVERY_CASES_CONSTANTS.PRIORITY_OPTIONS.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Reset Button */}
        <Button
          variant="outline"
          size="sm"
          onClick={onResetFilters}
          className="h-9 px-3 text-xs text-slate-600 hover:text-slate-900 border-slate-200 shadow-sm"
        >
          <RotateCcw className="w-3.5 h-3.5 mr-1 text-slate-400" />
          <span>{RECOVERY_CASES_CONSTANTS.FILTER_LABELS.RESET_FILTERS}</span>
        </Button>
      </div>
    </div>
  );
};
