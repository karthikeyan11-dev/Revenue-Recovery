/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ActionOutcome } from './ActionOutcome';
import type { ActionType } from './ActionType';
import type { PolicyDecision } from './PolicyDecision';
export type CaseActionItem = {
    id: string;
    proposed_action: ActionType;
    policy_decision: PolicyDecision;
    policy_reasoning?: (string | null);
    outcome: ActionOutcome;
    incentive_percent?: (number | null);
    created_at: string;
};

