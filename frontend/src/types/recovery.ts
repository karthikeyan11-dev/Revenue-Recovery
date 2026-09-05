import type {
  RecoveryCaseDetail,
  RecoveryCaseSummary,
  CasesListResponse,
  CaseStatus,
  ActionType,
  PolicyDecision,
  PromiseToPaySummary,
  PromiseEvaluationRequest,
  CaseTimelineItem,
  CaseActionItem,
} from '../api/generated';

export type {
  RecoveryCaseDetail,
  RecoveryCaseSummary,
  CasesListResponse,
  CaseStatus,
  ActionType,
  PolicyDecision,
  PromiseToPaySummary,
  PromiseEvaluationRequest,
  CaseTimelineItem,
  CaseActionItem,
};

export type RecoveryCaseResponse = RecoveryCaseSummary;
export type RecoveryCaseListResponse = CasesListResponse;
export type PromiseToPayResponse = PromiseToPaySummary;
export type EvaluatePromiseRequest = PromiseEvaluationRequest;

export interface RecoveryCaseFilterState {
  status?: string;
  segment?: string;
  failure_reason?: string;
  page?: number;
  page_size?: number;
}
