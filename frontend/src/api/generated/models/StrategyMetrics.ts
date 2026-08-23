/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Aggregate performance metrics for a simulation run.
 */
export type StrategyMetrics = {
    /**
     * Strategy identifier: BASELINE_RETRY_ONCE or AI_ORCHESTRATOR
     */
    strategy_name: string;
    /**
     * Total INR value of payment failures
     */
    total_revenue_at_risk: number;
    /**
     * Total INR successfully recovered
     */
    total_recovered_revenue: number;
    /**
     * Percentage of revenue recovered
     */
    recovery_rate_percent: number;
    /**
     * Total cost in INR (incentives + communication)
     */
    total_cost: number;
    /**
     * Net ROI percentage ((Recovered - Cost) / At Risk * 100)
     */
    net_roi_percent: number;
    /**
     * Total count of cases processed
     */
    cases_count: number;
    /**
     * Count of successfully recovered cases
     */
    recovered_cases_count: number;
    /**
     * Count of cases escalated to human review
     */
    escalated_cases_count: number;
    /**
     * Count of actions blocked by policy engine
     */
    rejected_actions_count: number;
};

