import type {
  Dispute,
  EvidenceItem,
  TimelineEvent,
  SettlementRecord,
  CaseStatusStep,
  IncentiveOffer,
  Party,
} from "@/types/dispute";

// ---------------------------------------------------------------------------
// Parties
// ---------------------------------------------------------------------------

export const mockCustomer: Party = {
  id: "cust_1001",
  name: "Priya Nair",
  role: "cardholder",
};

export const mockMerchant: Party = {
  id: "merch_2004",
  name: "Harborline Stays",
  role: "merchant",
};

// ---------------------------------------------------------------------------
// Disputes — a small list to populate dashboards, one "active" dispute
// used as the primary walkthrough for the Workspace / Evidence Board /
// Timeline / Settlement / Resolution pages.
// ---------------------------------------------------------------------------

export const mockDisputes: Dispute[] = [
  {
    id: "dsp_8841",
    transactionId: "txn_55291",
    merchant: mockMerchant,
    customer: mockCustomer,
    status: "IN_NEGOTIATION",
    reason: "Item not as described",
    amount: 340.0,
    currency: "USD",
    createdAt: "2026-07-18T14:12:00Z",
  },
  {
    id: "dsp_8790",
    transactionId: "txn_55110",
    merchant: mockMerchant,
    customer: mockCustomer,
    status: "RESOLVED",
    reason: "Duplicate charge",
    amount: 89.5,
    currency: "USD",
    createdAt: "2026-07-10T09:03:00Z",
  },
  {
    id: "dsp_8705",
    transactionId: "txn_54932",
    merchant: { id: "merch_3310", name: "Northgate Electronics", role: "merchant" },
    customer: mockCustomer,
    status: "OPEN",
    reason: "Item not received",
    amount: 212.75,
    currency: "USD",
    createdAt: "2026-07-21T18:47:00Z",
  },
  {
    id: "dsp_8622",
    transactionId: "txn_54810",
    merchant: mockMerchant,
    customer: { id: "cust_1077", name: "Devon Marsh", role: "cardholder" },
    status: "CLOSED",
    reason: "Service not rendered",
    amount: 150.0,
    currency: "USD",
    createdAt: "2026-06-30T11:22:00Z",
  },
];

export const primaryDispute = mockDisputes[0];

// ---------------------------------------------------------------------------
// Timeline — auto-generated chronology (Evidence Collector agent),
// the first thing either party sees on entering a session.
// ---------------------------------------------------------------------------

export const mockTimeline: TimelineEvent[] = [
  {
    id: "evt_1",
    disputeId: "dsp_8841",
    timestamp: "2026-07-12T10:02:00Z",
    title: "Booking confirmed",
    description: "Reservation made for a 2-night stay, Deluxe Harbor View room.",
  },
  {
    id: "evt_2",
    disputeId: "dsp_8841",
    timestamp: "2026-07-12T10:03:00Z",
    title: "Payment captured",
    description: "$340.00 charged to card ending 4471.",
  },
  {
    id: "evt_3",
    disputeId: "dsp_8841",
    timestamp: "2026-07-16T15:41:00Z",
    title: "Check-in recorded",
    description: "Guest checked in at property front desk.",
  },
  {
    id: "evt_4",
    disputeId: "dsp_8841",
    timestamp: "2026-07-16T16:20:00Z",
    title: "Guest message sent",
    description: "Guest messaged front desk: room did not match listing photos.",
  },
  {
    id: "evt_5",
    disputeId: "dsp_8841",
    timestamp: "2026-07-18T09:15:00Z",
    title: "Review posted",
    description: "Guest left a 2-star review citing room discrepancy.",
  },
  {
    id: "evt_6",
    disputeId: "dsp_8841",
    timestamp: "2026-07-18T14:12:00Z",
    title: "Dispute filed",
    description: "Cardholder opened a dispute: item not as described.",
  },
];

// ---------------------------------------------------------------------------
// Evidence board — tagged with credibility labels
// ---------------------------------------------------------------------------

export const mockEvidence: EvidenceItem[] = [
  {
    id: "ev_1",
    disputeId: "dsp_8841",
    uploader: "system",
    type: "SYSTEM_RECORD",
    credibility: "VERIFIED_TRANSACTION",
    summary: "Transaction record — $340.00 to Harborline Stays on Jul 12.",
    createdAt: "2026-07-18T14:12:05Z",
  },
  {
    id: "ev_2",
    disputeId: "dsp_8841",
    uploader: "system",
    type: "SYSTEM_RECORD",
    credibility: "TIMESTAMPED_RECEIPT",
    summary: "Booking confirmation — Deluxe Harbor View, 2 nights.",
    createdAt: "2026-07-18T14:12:06Z",
  },
  {
    id: "ev_3",
    disputeId: "dsp_8841",
    uploader: "cardholder",
    type: "IMAGE",
    credibility: "CUSTOMER_STATEMENT",
    summary: "Photo of the room actually provided at check-in.",
    filePath: "/demo-assets/room-photo.jpg",
    createdAt: "2026-07-18T14:20:00Z",
  },
  {
    id: "ev_4",
    disputeId: "dsp_8841",
    uploader: "merchant",
    type: "SYSTEM_RECORD",
    credibility: "GPS_CONFIRMED",
    summary: "Front-desk check-in log with device GPS confirmation.",
    createdAt: "2026-07-18T15:02:00Z",
  },
  {
    id: "ev_5",
    disputeId: "dsp_8841",
    uploader: "merchant",
    type: "TEXT",
    credibility: "MERCHANT_STATEMENT",
    summary: "Merchant statement: guest was offered a room change, declined.",
    createdAt: "2026-07-18T15:05:00Z",
  },
];

// ---------------------------------------------------------------------------
// Settlement — a small history so the panel can show it "evolving"
// ---------------------------------------------------------------------------

export const mockSettlementHistory: SettlementRecord[] = [
  {
    id: "st_1",
    disputeId: "dsp_8841",
    recommendation: "NO_REFUND",
    percentage: 0,
    reason: "Insufficient corroborating evidence at time of filing.",
    explanation:
      "Only the cardholder's statement was available when the dispute opened, so no refund could be recommended yet.",
    acceptedBy: null,
    updatedAt: "2026-07-18T14:13:00Z",
  },
  {
    id: "st_2",
    disputeId: "dsp_8841",
    recommendation: "PARTIAL_REFUND",
    percentage: 50,
    reason: "Room discrepancy corroborated by photo; check-in confirmed via GPS.",
    explanation:
      "The guest's photo shows a room inconsistent with the listing, and the merchant's GPS-confirmed check-in log verifies the stay occurred. A 50% refund reflects a valid discrepancy alongside a completed stay.",
    acceptedBy: null,
    updatedAt: "2026-07-18T15:06:00Z",
  },
];

export const currentSettlement = mockSettlementHistory[mockSettlementHistory.length - 1];

// ---------------------------------------------------------------------------
// Case status — user-facing steps for the sidebar
// ---------------------------------------------------------------------------

export const mockCaseStatus: CaseStatusStep[] = [
  { id: "cs_1", label: "Timeline Updated", state: "complete", timestamp: "2026-07-18T14:12:05Z" },
  { id: "cs_2", label: "Evidence Received", state: "complete", timestamp: "2026-07-18T14:20:00Z" },
  { id: "cs_3", label: "Merchant Response Received", state: "complete", timestamp: "2026-07-18T15:05:00Z" },
  { id: "cs_4", label: "AI Recommendation Ready", state: "complete", timestamp: "2026-07-18T15:06:00Z" },
  { id: "cs_5", label: "Dispute Resolved", state: "pending" },
];

// ---------------------------------------------------------------------------
// Incentive — merchant early-acceptance offer
// ---------------------------------------------------------------------------

export const mockIncentive: IncentiveOffer = {
  disputeId: "dsp_8841",
  active: true,
  windowEndsAt: "2026-07-19T14:12:00Z",
  description: "Accept within the window to reduce this dispute's processing fee by 50%.",
};

// ---------------------------------------------------------------------------
// Analyst view — aggregate stats across a merchant's dispute queue
// ---------------------------------------------------------------------------

export const mockAnalystStats = {
  openDisputes: 4,
  inNegotiation: 2,
  resolvedThisMonth: 11,
  avgResolutionTimeHours: 6.4,
  incentivesEarned: 5,
  trustScore: 87,
};
