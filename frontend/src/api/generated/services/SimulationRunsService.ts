/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GenerateDataRequest } from '../models/GenerateDataRequest';
import type { GenerateDataResponse } from '../models/GenerateDataResponse';
import type { RunStrategyRequest } from '../models/RunStrategyRequest';
import type { RunStrategyResponse } from '../models/RunStrategyResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class SimulationRunsService {
    /**
     * Generate synthetic cohort transactions and payment failure records
     * @param requestBody
     * @returns GenerateDataResponse Successful Response
     * @throws ApiError
     */
    public static generateSyntheticData(
        requestBody: GenerateDataRequest,
    ): CancelablePromise<GenerateDataResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/data/generate',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Run naive retry-once benchmark strategy against current failures
     * @param requestBody
     * @returns RunStrategyResponse Successful Response
     * @throws ApiError
     */
    public static runBaselineSimulation(
        requestBody: RunStrategyRequest,
    ): CancelablePromise<RunStrategyResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/run/baseline',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Run autonomous policy-governed multi-agent recovery workflow
     * @param requestBody
     * @returns RunStrategyResponse Successful Response
     * @throws ApiError
     */
    public static runAiOrchestratorSimulation(
        requestBody: RunStrategyRequest,
    ): CancelablePromise<RunStrategyResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/run/ai',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
