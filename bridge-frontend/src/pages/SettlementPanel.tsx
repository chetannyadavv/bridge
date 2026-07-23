import { useParams, useNavigate } from "react-router-dom";
import { SettlementRecommendationPanel } from "@/components/dispute/SettlementRecommendationPanel";
import { IncentiveBanner } from "@/components/dispute/IncentiveBanner";
import { Button } from "@/components/ui/Button";
import { useRole } from "@/lib/RoleContext";
import { mockSettlementHistory, mockIncentive } from "@/data/mockData";

export function SettlementPanel() {
  const { id } = useParams();
  const { role } = useRole();
  const navigate = useNavigate();

  const current = mockSettlementHistory[mockSettlementHistory.length - 1];
  const previous = mockSettlementHistory[mockSettlementHistory.length - 2];

  return (
    <div className="space-y-4">
      {role === "merchant" && <IncentiveBanner incentive={mockIncentive} />}

      <SettlementRecommendationPanel settlement={current} previous={previous} />

      <div className="flex items-center gap-2">
        <Button variant="settlement" onClick={() => navigate(`/disputes/${id}/resolution`)}>
          Accept settlement
        </Button>
        <Button variant="ghost" disabled title="Counter-offer — stretch goal, not in MVP scope">
          Counter-offer
        </Button>
      </div>

      <p className="font-mono text-[11px] text-ink-faint">
        Recommendation history: {mockSettlementHistory.length} revision(s) so far — the AI
        recommendation refreshes automatically whenever evidence changes.
      </p>
    </div>
  );
}
