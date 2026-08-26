import React from 'react';
import { Search } from 'lucide-react';

export interface CaseFiltersProps {
  searchTerm: string;
  onSearchChange: (value: string) => void;
  selectedStatus: string;
  onStatusChange: (status: string) => void;
}

export const CaseFilters: React.FC<CaseFiltersProps> = ({
  searchTerm,
  onSearchChange,
  selectedStatus,
  onStatusChange,
}) => {
  return (
    <div className="flex flex-wrap items-center gap-3">
      {/* Search bar */}
      <div className="relative">
        <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search customer, email, case..."
          className="pl-9 pr-4 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500 w-64"
        />
      </div>

      {/* Status Filter buttons */}
      <div className="flex items-center space-x-1 p-1 rounded-xl bg-slate-900 border border-slate-800">
        {(['ALL', 'RECOVERED', 'IN_PROGRESS', 'ESCALATED', 'BLOCKED', 'FAILED'] as const).map(
          (status) => (
            <button
              key={status}
              onClick={() => onStatusChange(status)}
              className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition ${
                selectedStatus === status
                  ? 'bg-brand-600 text-white font-semibold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {status === 'ALL' ? 'All' : status.replace('_', ' ')}
            </button>
          )
        )}
      </div>
    </div>
  );
};
