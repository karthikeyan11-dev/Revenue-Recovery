/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { StrategyMetrics } from './StrategyMetrics';
export type RunStrategyResponse = {
    status: string;
    strategy: string;
    cases_processed: number;
    metrics: StrategyMetrics;
    message: string;
};

