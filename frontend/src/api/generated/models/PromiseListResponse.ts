/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PromiseToPaySummary } from './PromiseToPaySummary';
/**
 * Response payload for promise listing with status aggregations.
 */
export type PromiseListResponse = {
    items: Array<PromiseToPaySummary>;
    total: number;
    pending_count: number;
    kept_count: number;
    broken_count: number;
};

