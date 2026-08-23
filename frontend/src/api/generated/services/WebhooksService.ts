/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class WebhooksService {
    /**
     * Razorpay Webhook Receiver
     * Receives, cryptographically validates, and processes authentic Razorpay webhook events.
     * - Validates HMAC-SHA256 signature against raw request body bytes.
     * - Idempotently prevents duplicate executions using event ID.
     * - Persists raw webhook payload for audit and forensics.
     * - Quickly acknowledges webhook (HTTP 200) and schedules LangGraph recovery in background.
     * - For payment.captured: closes active recovery cases and marks transaction SUCCESS.
     * @param xRazorpaySignature
     * @param xRazorpayEventId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static handleRazorpayWebhook(
        xRazorpaySignature?: (string | null),
        xRazorpayEventId?: (string | null),
    ): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/webhooks/razorpay',
            headers: {
                'X-Razorpay-Signature': xRazorpaySignature,
                'X-Razorpay-Event-Id': xRazorpayEventId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
