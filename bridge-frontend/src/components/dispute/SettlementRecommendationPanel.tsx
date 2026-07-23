import type { SettlementRecord } from "@/types/dispute";
import { Card, CardHeader, CardBody } from "@/components/ui/Card";
import { Scale } from "lucide-react";
import { cn, formatDateTime } from "@/lib/utils";

const recommendationLabel = {
  FULL_REFUND: "Full refund",
  PARTIAL_REFUND: "Partial refund",
  NO_REFUND: "No refund",
} as const;

export function SettlementRecommendationPanel({
  settlement,
  previous,
}: {
  settlement: SettlementRecord;
  previous?: SettlementRecord;
}) {
  const changed = previous && previous.recommendation !== settlement.recommendation;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Scale size={15} className="text-settlement" />
          <h3 className="font-display text-sm font-semibold text-ink">
            Settlement Recommendation
          </h3>
        </div>
        <span className="font-mono text-[11px] text-ink-faint">
          updated {formatDateTime(settlement.updatedAt)}
        </span>
      </CardHeader>
      <CardBody>
        <div className="flex items-baseline gap-3">
          <p className="font-display text-2xl font-semibold text-settlement">
            {recommendationLabel[settlement.recommendation]}
            {settlement.percentage !== null && settlement.recommendation === "PARTIAL_REFUND"
              ? ` — ${settlement.percentage}%`
              : ""}
          </p>
          {changed && (
            <span className="rounded-full bg-caution-tint px-2 py-0.5 font-mono text-[10px] text-[#7A5A1E]">
              revised
            </span>
          )}
        </div>

        <p className="mt-3 text-sm leading-relaxed text-ink-soft">{settlement.reason}</p>

        <div
          className={cn(
            "mt-4 rounded-md border border-hairline bg-paper px-3 py-2.5 text-sm text-ink-soft"
          )}
        >
          <p className="mb-1 font-mono text-[10px] uppercase tracking-wide text-ink-faint">
            Why this recommendation
          </p>
          {settlement.explanation}
        </div>

        {settlement.acceptedBy && settlement.acceptedBy.length > 0 && (
          <p className="mt-3 font-mono text-xs text-settlement">
            Accepted by: {settlement.acceptedBy.join(", ")}
          </p>
        )}
      </CardBody>
    </Card>
  );
}
