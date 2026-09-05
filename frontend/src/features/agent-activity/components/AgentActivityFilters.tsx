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
import { AGENT_ACTIVITY_CONSTANTS } from '../constants/agent-activity.constants';
import type { AgentActivityFiltersProps } from '../types/agent-activity.types';

export const AgentActivityFilters: React.FC<AgentActivityFiltersProps> = ({
  filters,
  onFilterChange,
  onResetFilters,
}) => {
  return (
    <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm flex flex-col md:flex-row items-center justify-between gap-3">
      {/* Search Input */}
      <div className="relative w-full md:w-80">
        <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
        <Input
          type="text"
          placeholder={AGENT_ACTIVITY_CONSTANTS.SEARCH_PLACEHOLDER}
          value={filters.search}
          onChange={(e) => onFilterChange('search', e.target.value)}
          className="pl-9 text-xs h-9 bg-slate-50 border-slate-200"
        />
      </div>

      {/* Select Filters */}
      <div className="flex items-center gap-3 w-full md:w-auto">
        <div className="w-36">
          <Select value={filters.status} onValueChange={(val) => onFilterChange('status', val)}>
            <SelectTrigger className="h-9 text-xs">
              <SelectValue placeholder={AGENT_ACTIVITY_CONSTANTS.STATUS_PLACEHOLDER} />
            </SelectTrigger>
            <SelectContent>
              {AGENT_ACTIVITY_CONSTANTS.STATUS_OPTIONS.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="w-40">
          <Select
            value={filters.time_range}
            onValueChange={(val) => onFilterChange('time_range', val)}
          >
            <SelectTrigger className="h-9 text-xs">
              <SelectValue placeholder={AGENT_ACTIVITY_CONSTANTS.TIME_RANGE_PLACEHOLDER} />
            </SelectTrigger>
            <SelectContent>
              {AGENT_ACTIVITY_CONSTANTS.TIME_RANGE_OPTIONS.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={onResetFilters}
          className="h-9 px-3 text-xs text-slate-600 border-slate-200 shadow-sm"
        >
          <RotateCcw className="w-3.5 h-3.5 mr-1 text-slate-400" />
          <span>{AGENT_ACTIVITY_CONSTANTS.RESET_BUTTON}</span>
        </Button>
      </div>
    </div>
  );
};
