import type {
  RecoveryCaseSummaryItem,
  RecoveryCaseDetail,
} from '../../../types/api.types';

export interface RecoveryCasesFiltersState {
  search: string;
  status: string;
  reason: string;
  priority: string;
}

export interface RecoveryCasesFiltersProps {
  filters: RecoveryCasesFiltersState;
  onFilterChange: (key: keyof RecoveryCasesFiltersState, value: string) => void;
  onResetFilters: () => void;
}

export interface RecoveryCasesTableProps {
  cases: RecoveryCaseSummaryItem[];
  total: number;
  inProgressCount: number;
  currentPage: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  onViewCase: (caseId: string) => void;
}

export interface RecoveryCaseDetailDrawerProps {
  caseDetail: RecoveryCaseDetail | null;
  isOpen: boolean;
  onClose: () => void;
}
