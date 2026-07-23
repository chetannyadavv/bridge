import { useParams, Link } from "react-router-dom";
import { AppShell, PageHeading } from "@/components/layout/AppShell";
import { Card, CardBody } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { mockDisputes, mockSettlementHistory } from "@/data/mockData";
import { formatCurrency, formatDateTime } from "@/lib/utils";
import { CheckCircle2 } from "lucide-react";

export function Resolution() {
  const { id } = useParams();
  const dispute = mockDisputes.find((d) => d.id === id) ?? mockDisputes[0];
  const settlement = mockSettlementHistory[mockSettlementHistory.length - 1];

  return (
    <AppShell>
      <PageHeading eyebrow="Module 16 · Resolution" title="Dispute resolved" />

      <Card className="max-w-2xl">
        <CardBody className="text-center">
          <CheckCircle2 size={36} className="mx-auto text-settlement" />
          <p className="mt-4 font-display text-3xl font-semibold text-settlement">
            Partial refund — {settlement.percentage}%
          </p>
          <p className="mt-1 text-sm text-ink-soft">
            {formatCurrency((dispute.amount * (settlement.percentage ?? 0)) / 100, dispute.currency)}{" "}
            of {formatCurrency(dispute.amount, dispute.currency)} on dispute {dispute.id}
          </p>

          <div className="mt-6 rounded-md border border-hairline bg-paper p-4 text-left text-sm text-ink-soft">
            <p className="mb-1 font-mono text-[10px] uppercase tracking-wide text-ink-faint">
              Why this outcome
            </p>
            {settlement.explanation}
          </div>

          <div className="mt-5 flex items-center justify-center gap-6 font-mono text-xs text-ink-faint">
            <span>Cardholder accepted</span>
            <span>Merchant accepted</span>
          </div>
          <p className="mt-1 font-mono text-[11px] text-ink-faint">
            Resolved {formatDateTime(settlement.updatedAt)}
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
