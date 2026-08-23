/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * System health check payload.
 */
export type HealthResponse = {
    /**
     * Health status: ok, degraded, or error
     */
    status: string;
    /**
     * FastAPI service status
     */
    service: string;
    /**
     * Database connectivity status
     */
    database: string;
    /**
     * Current application version
     */
    version: string;
    /**
     * Error message if degraded
     */
    error?: (string | null);
};

