/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PromiseEvaluationRequest } from '../models/PromiseEvaluationRequest';
import type { PromiseListResponse } from '../models/PromiseListResponse';
import type { PromiseStatus } from '../models/PromiseStatus';
import type { PromiseToPaySummary } from '../models/PromiseToPaySummary';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class PromiseToPayService {
    /**
     * List all tracked promises to pay
     * Retrieve paginated list of Promise-to-Pay records with aggregation counts.
     * @param limit
     * @param offset
     * @param status
     * @returns PromiseListResponse Successful Response
     * @throws ApiError
     */
    public static listPromises(
        limit: number = 100,
        offset?: number,
        status?: (PromiseStatus | null),
    ): CancelablePromise<PromiseListResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/promises',
            query: {
                'limit': limit,
                'offset': offset,
                'status': status,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Evaluate a promise as KEPT or BROKEN
     * Evaluates a pending payment promise.
     * - If KEPT (is_paid=True): Marks promise kept and completes case recovery.
     * - If BROKEN (is_paid=False): Re-invokes Strategist for exactly 1 follow-up, or forces human escalation if already followed up.
     * @param promiseId
     * @param requestBody
     * @returns PromiseToPaySummary Successful Response
     * @throws ApiError
     */
    public static evaluatePromise(
        promiseId: string,
        requestBody: PromiseEvaluationRequest,
    ): CancelablePromise<PromiseToPaySummary> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/promises/{promise_id}/evaluate',
            path: {
                'promise_id': promiseId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
