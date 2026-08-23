/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type RecoveryComparisonChartItem = {
    /**
     * Customer cohort or leak category
     */
    segment: string;
    /**
     * INR recovered under baseline
     */
    baseline_recovered_inr: number;
    /**
     * INR recovered under AI orchestrator
     */
    ai_recovered_inr: number;
    /**
     * Total at-risk revenue
     */
    total_at_risk_inr: number;
};

