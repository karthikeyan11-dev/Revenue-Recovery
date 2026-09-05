/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { HealthResponse } from '../models/HealthResponse';
import type { RootResponse } from '../models/RootResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class SystemService {
    /**
     * Root metadata endpoint
     * Root metadata endpoint.
     * @returns RootResponse Successful Response
     * @throws ApiError
     */
    public static getRoot(): CancelablePromise<RootResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/',
        });
    }
    /**
     * System health and database connectivity probe
     * Health check endpoint verifying system status and database connectivity.
     * Returns 200 with component statuses (service=online, database=connected/unreachable).
     * @returns HealthResponse Successful Response
     * @throws ApiError
     */
    public static getHealth(): CancelablePromise<HealthResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/health',
        });
    }
}
