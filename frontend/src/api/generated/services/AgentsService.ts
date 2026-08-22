/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AgentActivityFeedResponse } from '../models/AgentActivityFeedResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AgentsService {
    /**
     * Get recent agent reasoning activities and decision stream
     * @param limit Max activities to fetch
     * @returns AgentActivityFeedResponse Successful Response
     * @throws ApiError
     */
    public static getAgentActivityFeed(
        limit: number = 50,
    ): CancelablePromise<AgentActivityFeedResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/agents/activity',
            query: {
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
