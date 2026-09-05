/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { RecoveryComparisonChartItem } from './RecoveryComparisonChartItem';
import type { StrategyMetrics } from './StrategyMetrics';
/**
 * Headline metrics for the Executive Dashboard.
 */
export type DashboardMetricsResponse = {
    /**
     * Total INR value of payment leaks
     */
    total_revenue_at_risk: number;
    /**
     * Total INR recovered by AI Orchestrator
     */
    total_recovered_revenue: number;
    /**
     * AI recovery rate percentage
     */
    overall_recovery_rate: number;
    /**
     * Net ROI percentage after costs
     */
    net_roi_percent: number;
    /**
     * Baseline recovery rate percentage
     */
    baseline_recovery_rate: number;
    /**
     * Net additional INR won over baseline
     */
    recovery_uplift_inr: number;
    /**
     * Open and In-Progress recovery cases
     */
    active_cases_count: number;
    /**
     * Cases requiring human attention
     */
    escalated_cases_count: number;
    /**
     * Actions blocked or modified by policy gate
     */
    policy_interventions_count: number;
    /**
     * Segment-by-segment comparison
     */
    comparison_chart?: Array<RecoveryComparisonChartItem>;
    baseline_summary?: (StrategyMetrics | null);
    ai_summary?: (StrategyMetrics | null);
};

