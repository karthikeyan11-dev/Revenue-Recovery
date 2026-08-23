/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type RunStrategyRequest = {
    /**
     * Optional limit on cases to process in this run
     */
    limit?: (number | null);
    /**
     * Use fast deterministic mock LLM predictions for local demo runs if API key absent
     */
    use_mock_llm?: boolean;
};

