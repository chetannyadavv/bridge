import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { AppShell, PageHeading } from "@/components/layout/AppShell";
import { Card, CardBody } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { recommendationLabel } from "@/components/dispute/SettlementRecommendationPanel";
import { useDisputes } from "@/lib/DisputeContext";
import { formatCurrency, formatDateTime, cn } from "@/lib/utils";
import { CheckCircle2 } from "lucide-react";

export function Resolution() {
  const { id } = useParams();
  const { getDispute, getSettlementHistory, loadDispute } = useDisputes();
  const [isLoading, setIsLoading] = useState(true);

  // Resolution isn't nested under Workspace's route, so a direct visit
  // (e.g. a page refresh on this URL) may not have loaded this dispute's
  // data yet — load it defensively here too.
  useEffect(() => {
    if (!id) return;
    setIsLoading(true);
    loadDispute(id).finally(() => setIsLoading(false));
  }, [id, loadDispute]);

  const dispute = getDispute(id ?? "");
  const history = getSettlementHistory(id ?? "");
  const settlement = history[history.length - 1];

  if (isLoading) {
    return (
      <AppShell>
        <p className="text-sm text-ink-faint">Loading…</p>
      </AppShell>
    );
  }

  if (!dispute || !settlement) {
    return (
      <AppShell>
        <PageHeading
          eyebrow="Module 16 · Resolution"
          title="Nothing to resolve yet"
          description="This dispute doesn't have a settlement recommendation to show yet. Add evidence and accept a recommendation from the Settlement tab first."
        />
        <Link to="/analyst">
          <Button variant="secondary">Back to dashboard</Button>
        </Link>
      </AppShell>
    );
  }

  const refundAmount = (dispute.amount * (settlement.percentage ?? 0)) / 100;
  const cardholderAccepted = settlement.acceptedBy?.includes("cardholder") ?? false;
  const merchantAccepted = settlement.acceptedBy?.includes("merchant") ?? false;

  return (
    <AppShell>
      <PageHeading eyebrow="Module 16 · Resolution" title="Dispute resolved" />

      <Card className="max-w-2xl">
        <CardBody className="text-center">
          <CheckCircle2 size={36} className="mx-auto text-settlement" />
          <p className="mt-4 font-display text-3xl font-semibold text-settlement">
            {recommendationLabel[settlement.recommendation]}
            {settlement.recommendation === "PARTIAL_REFUND" ? ` — ${settlement.percentage}%` : ""}
          </p>
          <p className="mt-1 text-sm text-ink-soft">
            {formatCurrency(refundAmount, dispute.currency)} of{" "}
            {formatCurrency(dispute.amount, dispute.currency)} on dispute {dispute.id}
          </p>

          <div className="mt-6 rounded-md border border-hairline bg-paper p-4 text-left text-sm text-ink-soft">
            <p className="mb-1 font-mono text-[10px] uppercase tracking-wide text-ink-faint">
              Why this outcome
            </p>
            {settlement.explanation}
          </div>

          <div className="mt-5 flex items-center justify-center gap-6 font-mono text-xs">
            <span className={cn(cardholderAccepted ? "text-settlement" : "text-ink-faint")}>
              Cardholder {cardholderAccepted ? "accepted" : "pending"}
            </span>
            <span className={cn(merchantAccepted ? "text-settlement" : "text-ink-faint")}>
              Merchant {merchantAccepted ? "accepted" : "pending"}
            </span>
          </div>
          <p className="mt-1 font-mono text-[11px] text-ink-faint">
            Updated {formatDateTime(settlement.updatedAt)}
          </p>
        </CardBody>
      </Card>

      <div className="mt-6 flex gap-3">
        <Link to="/analyst">
          <Button variant="secondary">Back to dashboard</Button>
        </Link>
        <Link to="/disputes/new">
          <Button variant="ghost">Open another dispute</Button>
        </Link>
      </div>
    </AppShell>
  );
}
