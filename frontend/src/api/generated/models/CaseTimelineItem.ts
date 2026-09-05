/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type CaseTimelineItem = {
    id: string;
    agent: string;
    step_name: string;
    input_summary: string;
    output_summary: string;
    decision?: (string | null);
    confidence: number;
    empirical_confidence?: (number | null);
    llm_stated_confidence?: (number | null);
    precedent_sample_size?: (number | null);
    timestamp: string;
};

