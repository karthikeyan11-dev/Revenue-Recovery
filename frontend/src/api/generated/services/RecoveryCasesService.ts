/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CasesListResponse } from '../models/CasesListResponse';
import type { CaseStatus } from '../models/CaseStatus';
import type { RecoveryCaseDetail } from '../models/RecoveryCaseDetail';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class RecoveryCasesService {
    /**
     * List recovery cases with filtering and pagination
     * @param status Filter by case status
     * @param limit Items per page
     * @param offset Pagination offset
     * @returns CasesListResponse Successful Response
     * @throws ApiError
     */
    public static listRecoveryCases(
        status?: (CaseStatus | null),
        limit: number = 50,
        offset?: number,
    ): CancelablePromise<CasesListResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/cases',
            query: {
                'status': status,
                'limit': limit,
                'offset': offset,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get comprehensive recovery case detail with actions and timeline
     * @param caseId
     * @returns RecoveryCaseDetail Successful Response
     * @throws ApiError
     */
    public static getRecoveryCaseDetail(
        caseId: string,
    ): CancelablePromise<RecoveryCaseDetail> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/cases/{case_id}',
            path: {
                'case_id': caseId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
