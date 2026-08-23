/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type AgentActivityItem = {
    id: string;
    case_id: string;
    /**
     * Agent name: Detective, Intelligence, Strategist, Policy, Executor, Analyst
     */
    agent: string;
    step_name: string;
    input_summary: string;
    output_summary: string;
    decision?: (string | null);
    confidence: number;
    timestamp: string;
};

