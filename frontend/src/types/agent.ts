import type {
  AgentActivityFeedResponse,
  AgentActivityItem,
  LeakType,
  ActionType,
  PolicyDecision,
} from '../api/generated';

export type {
  AgentActivityFeedResponse,
  AgentActivityItem,
};

export interface RevenueDetectiveOutput {
  failure_id: string;
  leak_type: LeakType;
  amount: number;
  confidence: number;
  recoverability_score: number;
  reasoning: string;
  precedent_sample_size?: number;
  llm_stated_confidence?: number;
}

export interface CustomerIntelligenceOutput {
  customer_id: string;
  payer_reliability_score: number;
  total_past_transactions?: number;
  successful_past_transactions?: number;
  timing_band?: string;
  hours_since_failure?: number;
  recent_failure_count?: number;
  has_alternate_rail?: boolean;
  alternate_rails?: string[];
  available_channels: string[];
  confidence: number;
  insights: string;
  precedent_sample_size?: number;
  llm_stated_confidence?: number;
}

export interface ProposedRecoveryAction {
  action_type: ActionType;
  retry_delay_hours?: number | null;
  channel?: string | null;
  incentive_percent?: number | null;
  insufficient_precedent?: boolean;
  retrieved_precedent_count?: number;
  confidence?: number;
  llm_stated_confidence?: number;
  reasoning: string;
}

export interface PolicyEvaluationOutput {
  decision: PolicyDecision;
  violated_rule?: string | null;
  reasoning: string;
}
