// Types mirror Architecture v1.1 §6 Database and the frozen product spec.
// This is a frontend-only skeleton — all data below is mocked, no network
// or persistence layer is implied by these shapes.

export type DisputeStatus = "OPEN" | "IN_NEGOTIATION" | "RESOLVED" | "CLOSED";

export type Role = "cardholder" | "merchant";

export interface Party {
  id: string;
  name: string;
  role: Role;
}

export interface Dispute {
  id: string;
  transactionId: string;
  merchant: Party;
  customer: Party;
  status: DisputeStatus;
  reason: string;
  amount: number;
  currency: string;
  createdAt: string;
}

export type CredibilityLabel =
  | "VERIFIED_TRANSACTION"
  | "GPS_CONFIRMED"
  | "TIMESTAMPED_RECEIPT"
  | "CUSTOMER_STATEMENT"
  | "MERCHANT_STATEMENT"
  | "UNVERIFIED";

export type EvidenceType = "IMAGE" | "PDF" | "TEXT" | "SYSTEM_RECORD";

export interface EvidenceItem {
  id: string;
  disputeId: string;
  uploader: Role | "system";
  type: EvidenceType;
  credibility: CredibilityLabel;
  summary: string;
  filePath?: string;
  createdAt: string;
}

export interface TimelineEvent {
  id: string;
  disputeId: string;
  timestamp: string;
  title: string;
  description: string;
}

export type SettlementRecommendationType =
  | "FULL_REFUND"
  | "PARTIAL_REFUND"
  | "NO_REFUND";

export interface SettlementRecord {
  id: string;
  disputeId: string;
  recommendation: SettlementRecommendationType;
  percentage: number | null;
  reason: string;
  explanation: string;
  acceptedBy: Role[] | null;
  updatedAt: string;
}

export type CaseStatusState = "pending" | "in_progress" | "complete";

export interface CaseStatusStep {
  id: string;
  label: string;
  state: CaseStatusState;
  timestamp?: string;
}

export interface IncentiveOffer {
  disputeId: string;
  active: boolean;
  windowEndsAt: string;
  description: string;
}
