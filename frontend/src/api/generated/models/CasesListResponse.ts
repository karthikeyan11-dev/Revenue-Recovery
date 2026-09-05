/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { RecoveryCaseSummary } from './RecoveryCaseSummary';
export type CasesListResponse = {
    items: Array<RecoveryCaseSummary>;
    total: number;
    open_count: number;
    recovered_count: number;
    escalated_count: number;
    failed_count: number;
};

