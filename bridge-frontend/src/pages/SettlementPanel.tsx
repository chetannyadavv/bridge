import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { SettlementRecommendationPanel } from "@/components/dispute/SettlementRecommendationPanel";
import { IncentiveBanner } from "@/components/dispute/IncentiveBanner";
import { Button } from "@/components/ui/Button";
import { useRole } from "@/lib/RoleContext";
import { useDisputes } from "@/lib/DisputeContext";
import { mockIncentive } from "@/data/mockData";

export function SettlementPanel() {
  const { id } = useParams();
  const { role } = useRole();
  const navigate = useNavigate();
  const { getSettlementHistory, acceptSettlement } = useDisputes();
  const [isAccepting, setIsAccepting] = useState(false);

  const history = getSettlementHistory(id ?? "");
  const current = history[history.length - 1];
  const previous = history[history.length - 2];

  async function handleAccept() {
    if (!id) return;
    setIsAccepting(true);
    try {
      await acceptSettlement(id, role);
      navigate(`/disputes/${id}/resolution`);
    } catch {
      setIsAccepting(false);
    }
  }

  if (!current) {
    return (
      <div className="rounded-md border border-hairline bg-paper px-3 py-2.5 text-sm text-ink-soft">
        No recommendation yet — add evidence from both sides to generate one.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {role === "merchant" && <IncentiveBanner incentive={mockIncentive} />}

      <SettlementRecommendationPanel settlement={current} previous={previous} />

      <div className="flex items-center gap-2">
        <Button variant="settlement" onClick={handleAccept} disabled={isAccepting}>
          {isAccepting ? "Accepting…" : "Accept settlement"}
        </Button>
        <Button variant="ghost" disabled title="Counter-offer — stretch goal, not in MVP scope">
          Counter-offer
        </Button>
      </div>

      <p className="font-mono text-[11px] text-ink-faint">
        Recommendation history: {history.length} revision(s) so far — the AI
        recommendation refreshes automatically whenever evidence changes.
      </p>
    </div>
  );
}
