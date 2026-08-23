/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PromiseStatus } from './PromiseStatus';
/**
 * Pydantic summary schema for a Promise-to-Pay record.
 */
export type PromiseToPaySummary = {
    id: string;
    case_id: string;
    customer_id?: (string | null);
    customer_name?: string;
    customer_email?: string;
    customer_segment?: string;
    committed_amount: number;
    committed_date: string;
    status: PromiseStatus;
    follow_up_count?: number;
    created_at: string;
    resolved_at?: (string | null);
};

