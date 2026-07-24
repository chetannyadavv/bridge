import type { IncentiveOffer } from "@/types/dispute";

// Sprint 3: disputes, evidence, timeline events, and settlement history
// are now owned by the backend (see src/services/*) and no longer live
// here. What remains is content the backend doesn't model yet and that
// Sprint 3 didn't ask to make dynamic — the merchant incentive banner
// and the Analyst View's aggregate stats tile row.

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
