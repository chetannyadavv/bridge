import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { AppShell, PageHeading } from "@/components/layout/AppShell";
import { Card, CardBody } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { EvidenceCard } from "@/components/dispute/EvidenceCard";
import { ConfidenceMeter } from "@/components/dispute/ConfidenceMeter";
import { recommendationLabel } from "@/components/dispute/SettlementRecommendationPanel";
import { useDisputes } from "@/lib/DisputeContext";
import { formatCurrency, formatDateTime, cn } from "@/lib/utils";
import {
  CheckCircle2,
  XCircle,
  Scale,
  AlertTriangle,
  FileQuestion,
} from "lucide-react";

const OUTCOME_STYLE: Record<
  string,
  { icon: typeof CheckCircle2; color: string; bg: string }
> = {
  "Approve Refund": { icon: CheckCircle2, color: "text-settlement", bg: "bg-settlement-tint" },
  "Partial Refund": { icon: Scale, color: "text-settlement", bg: "bg-settlement-tint" },
  "Reject Refund": { icon: XCircle, color: "text-merchant", bg: "bg-merchant-tint" },
  "Request Additional Evidence": {
    icon: FileQuestion,
    color: "text-[#7A5A1E]",
    bg: "bg-caution-tint",
  },
  "Escalate for Manual Review": { icon: AlertTriangle, color: "text-ink", bg: "bg-black/[0.05]" },
};

export function Resolution() {
  const { id } = useParams();
  const { getDispute, getSettlementHistory, getEvidence, loadDispute } = useDisputes();
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);

  function load() {
    if (!id) return;
    setIsLoading(true);
    setLoadError(false);
    loadDispute(id)
      .catch(() => setLoadError(true))
      .finally(() => setIsLoading(false));
  }

  // Resolution isn't nested under Workspace's route, so a direct visit
  // (e.g. a page refresh on this URL) may not have loaded this dispute's
  // data yet — load it defensively here too.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(load, [id, loadDispute]);

  const dispute = getDispute(id ?? "");
  const history = getSettlementHistory(id ?? "");
  const settlement = history[history.length - 1];
  const evidence = getEvidence(id ?? "");

  if (isLoading) {
    return (
      <AppShell>
        <div className="flex items-center gap-2 text-sm text-ink-faint">
          <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-ink-faint border-t-transparent" />
          Loading resolution…
        </div>
      </AppShell>
    );
  }

  if (loadError) {
    return (
      <AppShell>
        <div className="rounded-[var(--radius-card)] border border-cardholder/30 bg-cardholder-tint/30 p-8 text-center">
          <p className="font-display text-lg font-semibold text-ink">Couldn't load this resolution</p>
          <p className="mt-1 text-sm text-ink-soft">
            The server may be unreachable. Check your connection and try again.
          </p>
          <div className="mt-4 flex justify-center gap-2">
            <Button variant="settlement" size="sm" onClick={load}>
              Try again
            </Button>
            <Link to="/analyst">
              <Button variant="secondary" size="sm">
                Back to dashboard
              </Button>
            </Link>
          </div>
        </div>
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

  const isResolved = dispute.status === "RESOLVED" || dispute.status === "CLOSED";

  if (!isResolved) {
    return (
      <AppShell>
        <PageHeading
          eyebrow="Module 16 · Resolution"
          title="Not yet resolved"
          description="A settlement recommendation exists for this dispute, but neither party has accepted it yet. Nothing has been finalized."
        />
        <Card className="max-w-2xl">
          <CardBody>
            <p className="mb-1 font-mono text-[10px] uppercase tracking-wide text-ink-faint">
              Current recommendation
            </p>
            <p className="font-display text-xl font-semibold text-ink">
              {recommendationLabel[settlement.recommendation]}
              {settlement.recommendation === "PARTIAL_REFUND" ? ` — ${settlement.percentage}%` : ""}
            </p>
          </CardBody>
        </Card>
        <div className="mt-6 flex gap-3">
          <Link to={`/disputes/${dispute.id}/settlement`}>
            <Button variant="settlement">Review and accept on the Settlement tab</Button>
          </Link>
          <Link to="/analyst">
            <Button variant="secondary">Back to dashboard</Button>
          </Link>
        </div>
      </AppShell>
    );
  }

  const refundAmount = (dispute.amount * (settlement.percentage ?? 0)) / 100;
  const cardholderAccepted = settlement.acceptedBy?.includes("cardholder") ?? false;
  const merchantAccepted = settlement.acceptedBy?.includes("merchant") ?? false;

  const outcomeKey = settlement.engineRecommendation ?? recommendationLabel[settlement.recommendation];
  const outcome = OUTCOME_STYLE[outcomeKey] ?? OUTCOME_STYLE["Escalate for Manual Review"];
  const OutcomeIcon = outcome.icon;

  const missingCardholder = (settlement.missingEvidence ?? []).filter((m) => m.startsWith("Cardholder:"));
  const missingMerchant = (settlement.missingEvidence ?? []).filter((m) => m.startsWith("Merchant:"));
  const hasMissingEvidence = missingCardholder.length > 0 || missingMerchant.length > 0;

  return (
    <AppShell>
      <PageHeading eyebrow="Module 16 · Resolution" title="Dispute resolved" />

      {/* Headline — understandable within a few seconds */}
      <Card className="max-w-3xl">
        <CardBody>
          <div className="flex items-start gap-4">
            <div className={cn("rounded-full p-3", outcome.bg)}>
              <OutcomeIcon size={28} className={outcome.color} />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-3">
                <p className={cn("font-display text-2xl font-semibold", outcome.color)}>
                  {outcomeKey}
                  {settlement.recommendation === "PARTIAL_REFUND" ? ` — ${settlement.percentage}%` : ""}
                </p>
                {typeof settlement.confidence === "number" && (
                  <ConfidenceMeter confidence={settlement.confidence} />
                )}
              </div>

              <p className="mt-1 text-sm text-ink-soft">
                {formatCurrency(refundAmount, dispute.currency)} of{" "}
                {formatCurrency(dispute.amount, dispute.currency)} on dispute {dispute.id}
              </p>

              {(settlement.reasonCode || settlement.category) && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {settlement.reasonCode && (
                    <span className="rounded-full bg-black/[0.05] px-2.5 py-1 font-mono text-[11px] text-ink-soft">
                      Reason code {settlement.reasonCode}
                    </span>
                  )}
                  {settlement.category && (
                    <span className="rounded-full bg-black/[0.05] px-2.5 py-1 font-mono text-[11px] text-ink-soft">
                      {settlement.category}
                    </span>
                  )}
                </div>
              )}

              {settlement.summary && (
                <p className="mt-4 text-sm leading-relaxed text-ink">{settlement.summary}</p>
              )}
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Evidence considered + missing evidence, side by side */}
      <div className="mt-4 grid max-w-3xl grid-cols-1 gap-4 md:grid-cols-2">
        <Card>
          <CardBody>
            <p className="mb-3 font-mono text-xs uppercase tracking-wide text-ink-faint">
              Evidence considered ({evidence.length})
            </p>
            {evidence.length === 0 ? (
              <p className="text-sm text-ink-faint">No evidence was submitted before this decision.</p>
            ) : (
              <div className="space-y-2">
                {evidence.map((item) => (
                  <EvidenceCard key={item.id} evidence={item} />
                ))}
              </div>
            )}
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <p className="mb-3 font-mono text-xs uppercase tracking-wide text-ink-faint">
              Missing evidence
            </p>
            {!hasMissingEvidence ? (
              <p className="text-sm text-settlement">
                Both sides fully documented their position — nothing outstanding.
              </p>
            ) : (
              <div className="space-y-3">
                <div>
                  <p className="mb-1 text-xs font-medium text-cardholder">Cardholder</p>
                  {missingCardholder.length === 0 ? (
                    <p className="text-xs text-ink-faint">Nothing outstanding.</p>
                  ) : (
                    <ul className="space-y-1">
                      {missingCardholder.map((m) => (
                        <li key={m} className="text-sm text-ink-soft">
                          {m.replace("Cardholder: ", "")}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
                <div>
                  <p className="mb-1 text-xs font-medium text-merchant">Merchant</p>
                  {missingMerchant.length === 0 ? (
                    <p className="text-xs text-ink-faint">Nothing outstanding.</p>
                  ) : (
                    <ul className="space-y-1">
                      {missingMerchant.map((m) => (
                        <li key={m} className="text-sm text-ink-soft">
                          {m.replace("Merchant: ", "")}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            )}
          </CardBody>
        </Card>
      </div>

      {/* Why this outcome + next steps */}
      <div className="mt-4 grid max-w-3xl grid-cols-1 gap-4 md:grid-cols-2">
        <Card>
          <CardBody>
            <p className="mb-2 font-mono text-xs uppercase tracking-wide text-ink-faint">
              Why this outcome
            </p>
            {settlement.reasons && settlement.reasons.length > 0 ? (
              <ul className="space-y-1.5">
                {settlement.reasons.map((r) => (
                  <li key={r} className="flex gap-2 text-sm text-ink-soft">
                    <span className="text-ink-faint">·</span>
                    {r}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-ink-soft">{settlement.explanation}</p>
            )}
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <p className="mb-2 font-mono text-xs uppercase tracking-wide text-ink-faint">Next steps</p>
            {settlement.nextSteps && settlement.nextSteps.length > 0 ? (
              <ul className="space-y-1.5">
                {settlement.nextSteps.map((step) => (
                  <li key={step} className="flex gap-2 text-sm text-ink-soft">
                    <CheckCircle2 size={14} className="mt-0.5 shrink-0 text-ink-faint" />
                    {step}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-ink-faint">No further action recorded.</p>
            )}
          </CardBody>
        </Card>
      </div>

      {/* Acceptance status */}
      <Card className="mt-4 max-w-3xl">
        <CardBody>
          <div className="flex flex-wrap items-center justify-center gap-6 font-mono text-xs">
            <span className={cn(cardholderAccepted ? "text-settlement" : "text-ink-faint")}>
              Cardholder {cardholderAccepted ? "accepted" : "pending"}
            </span>
            <span className={cn(merchantAccepted ? "text-settlement" : "text-ink-faint")}>
              Merchant {merchantAccepted ? "accepted" : "pending"}
            </span>
          </div>
          <p className="mt-1 text-center font-mono text-[11px] text-ink-faint">
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
