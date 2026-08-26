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
  segment: CustomerSegment;
  ltv: number;
  churn_probability: number;
  preferred_channel: CommunicationChannel;
}
