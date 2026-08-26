import React, { useState } from 'react';
import { useRecoveryCases } from '../hooks/useRecoveryCases';
import { CaseFilters } from '../components/CaseFilters';
import { CasesTable } from '../components/CasesTable';
import { CaseDetailDrawer } from '../components/CaseDetailDrawer';
import type { CaseStatus, RecoveryCaseResponse } from '../../../types/recovery';

export const RecoveryCasesContainer: React.FC = () => {
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);

  const { data: casesData, isLoading } = useRecoveryCases({
    status: selectedStatus === 'ALL' ? undefined : (selectedStatus as CaseStatus),
    limit: 100,
  });

  const filteredItems = (casesData?.items || []).filter((item: RecoveryCaseResponse) => {
    if (!searchTerm.trim()) return true;
    const term = searchTerm.toLowerCase();
    return (
      item.id.toLowerCase().includes(term) ||
      item.customer_name.toLowerCase().includes(term) ||
      item.customer_email.toLowerCase().includes(term) ||
      item.customer_segment.toLowerCase().includes(term)
    );
  });

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-[#0c2340]/90 border border-slate-800 backdrop-blur shadow-xl">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">
            Recovery Cases Management
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Browse payment failure events, examine empirical precedent grounds, inspect policy gates, and monitor promises-to-pay.
          </p>
        </div>

        <CaseFilters
          searchTerm={searchTerm}
          onSearchChange={setSearchTerm}
          selectedStatus={selectedStatus}
          onStatusChange={setSelectedStatus}
        />
      </div>

      {/* Cases Table */}
      <CasesTable
        cases={filteredItems}
        isLoading={isLoading}
        onSelectCase={setSelectedCaseId}
      />

      {/* Case Detail Slide-over Modal */}
      <CaseDetailDrawer
        caseId={selectedCaseId}
        onClose={() => setSelectedCaseId(null)}
      />
    </div>
  );
};
