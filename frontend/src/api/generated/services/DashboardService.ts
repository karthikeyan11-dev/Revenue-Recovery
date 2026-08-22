/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DashboardMetricsResponse } from '../models/DashboardMetricsResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DashboardService {
    /**
     * Get executive dashboard recovery headline numbers and comparison chart
     * @returns DashboardMetricsResponse Successful Response
     * @throws ApiError
     */
    public static getDashboardSummary(): CancelablePromise<DashboardMetricsResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/dashboard/summary',
        });
    }
}
