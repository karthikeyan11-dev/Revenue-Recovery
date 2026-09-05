import React, { useState } from 'react';
import { RefreshCw, AlertTriangle } from 'lucide-react';
import { Button } from '../../../components/ui/button';
import { RecoveryCaseDetailDrawer } from '../components/RecoveryCaseDetailDrawer';
import { RecoveryCasesFilters } from '../components/RecoveryCasesFilters';
import { RecoveryCasesTable } from '../components/RecoveryCasesTable';
import { useGetRecoveryCases } from '../hooks/useGetRecoveryCases';
import { LogoLoader } from '../../../components/common/LogoLoader';
import type { RecoveryCasesFiltersState } from '../types/recovery-cases.types';

const INITIAL_FILTERS: RecoveryCasesFiltersState = {
  search: '',
  status: 'all',
  reason: 'all',
  priority: 'all',
};

export const RecoveryCasesContainer: React.FC = () => {
  const [filters, setFilters] = useState<RecoveryCasesFiltersState>(INITIAL_FILTERS);
  const [page, setPage] = useState<number>(1);
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState<boolean>(false);

  const pageSize = 10;
  const { casesData, caseDetail, isLoading, isError, error, refetch } = useGetRecoveryCases(
    filters,
    page,
    pageSize,
    selectedCaseId
  );

  const handleFilterChange = (key: keyof RecoveryCasesFiltersState, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setPage(1);
  };

  const handleResetFilters = () => {
    setFilters(INITIAL_FILTERS);
    setPage(1);
  };

  const handleViewCase = (caseId: string) => {
    setSelectedCaseId(caseId);
    setIsDrawerOpen(true);
  };

  const handleCloseDrawer = () => {
    setIsDrawerOpen(false);
  };

  if (isError) {
    return (
      <div className="p-8 bg-white border border-rose-200 rounded-xl shadow-sm text-center space-y-4">
        <div className="w-12 h-12 rounded-full bg-rose-50 text-rose-600 flex items-center justify-center mx-auto">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <div className="text-base font-semibold text-slate-900">Failed to load Recovery Cases</div>
        <p className="text-xs text-slate-500 max-w-md mx-auto">
          {(error as Error)?.message || 'An unexpected error occurred.'}
        </p>
        <Button onClick={() => refetch()} variant="outline" size="sm" className="space-x-2">
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Retry Connection</span>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 1. Filters Row */}
      <RecoveryCasesFilters
        filters={filters}
        onFilterChange={handleFilterChange}
        onResetFilters={handleResetFilters}
      />

      {/* 2. Cases Table */}
      {isLoading ? (
        <LogoLoader variant="table" label="Retrieving live recovery case ledger..." />
      ) : (
        <RecoveryCasesTable
          cases={casesData?.items || []}
          total={casesData?.total || 0}
          inProgressCount={casesData?.in_progress_count || 0}
          currentPage={page}
          pageSize={pageSize}
          onPageChange={setPage}
          onViewCase={handleViewCase}
        />
      )}

      {/* 3. Detail Drawer */}
      <RecoveryCaseDetailDrawer
        caseDetail={caseDetail || null}
        isOpen={isDrawerOpen}
        onClose={handleCloseDrawer}
      />
    </div>
  );
};
