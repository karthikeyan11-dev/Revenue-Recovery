import type {
  CustomerSegment,
} from '../api/generated';

export type {
  CustomerSegment,
};

export type CommunicationChannel = 'WHATSAPP' | 'EMAIL' | 'SMS' | 'CALL' | 'NONE';

export interface CustomerProfileResponse {
  id: string;
  name: string;
  email: string;
  phone?: string | null;
  payer_reliability_score?: number;
  available_channels?: string[];
  total_past_transactions?: number;
  successful_past_transactions?: number;
}
