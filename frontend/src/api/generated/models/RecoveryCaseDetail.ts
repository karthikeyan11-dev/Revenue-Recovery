/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CaseActionItem } from './CaseActionItem';
import type { CaseStatus } from './CaseStatus';
import type { CaseTimelineItem } from './CaseTimelineItem';
import type { CustomerSegment } from './CustomerSegment';
import type { LeakType } from './LeakType';
import type { PromiseToPaySummary } from './PromiseToPaySummary';
export type RecoveryCaseDetail = {
    id: string;
    customer_id: string;
    customer_name: string;
    customer_email: string;
    customer_segment: CustomerSegment;
    leak_type: LeakType;
    leak_amount: number;
    recoverability_score: number;
    status: CaseStatus;
    recovered_amount: number;
    recovery_cost: number;
    has_sufficient_precedent?: boolean;
    precedent_count?: number;
    promise_status?: (string | null);
    created_at: string;
    resolved_at?: (string | null);
    actions?: Array<CaseActionItem>;
    timeline?: Array<CaseTimelineItem>;
    promises?: Array<PromiseToPaySummary>;
};

