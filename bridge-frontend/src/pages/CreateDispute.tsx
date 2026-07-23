import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { AppShell, PageHeading } from "@/components/layout/AppShell";
import { Card, CardBody } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { primaryDispute } from "@/data/mockData";
import { formatCurrency, formatDateTime } from "@/lib/utils";

const reasons = [
  "Item not received",
  "Item not as described",
  "Duplicate charge",
  "Service not rendered",
  "Unauthorized transaction",
  "Other",
];

// Placeholder transaction list — in the real system this comes from the
// cardholder's transaction history via the Session Service.
const mockTransactions = [
  { id: "txn_55291", merchant: "Harborline Stays", amount: 340.0, date: "2026-07-12T10:03:00Z" },
  { id: "txn_55340", merchant: "Northgate Electronics", amount: 212.75, date: "2026-07-19T08:20:00Z" },
  { id: "txn_55402", merchant: "Riverside Bistro", amount: 64.2, date: "2026-07-20T19:45:00Z" },
];

export function CreateDispute() {
  const navigate = useNavigate();
  const [selectedTxn, setSelectedTxn] = useState<string | null>(mockTransactions[0].id);
  const [reason, setReason] = useState<string>(reasons[1]);

  function handleSubmit() {
    // Mock-only: routes straight into the seeded demo workspace regardless
    // of selection. Real submission is owned by the Session Service.
    navigate(`/disputes/${primaryDispute.id}`);
  }

  return (
    <AppShell>
      <PageHeading
        eyebrow="Module 1 · Dispute Intake"
        title="Open a dispute"
        description="Pick the charge and a reason. No essay required — the timeline builds itself."
      />

      <div className="grid grid-cols-1 gap-6 md:grid-cols-[1.3fr_1fr]">
        <Card>
          <CardBody>
            <p className="mb-3 font-mono text-xs uppercase tracking-wide text-ink-faint">
              1. Select a transaction
            </p>
            <div className="space-y-2">
              {mockTransactions.map((txn) => (
                <button
                  key={txn.id}
                  onClick={() => setSelectedTxn(txn.id)}
                  className={`focus-ring flex w-full items-center justify-between rounded-md border px-3.5 py-3 text-left transition-colors ${
                    selectedTxn === txn.id
                      ? "border-navy bg-black/[0.02]"
                      : "border-hairline hover:border-ink-faint"
                  }`}
                >
                  <div>
                    <p className="text-sm font-medium text-ink">{txn.merchant}</p>
                    <p className="font-mono text-[11px] text-ink-faint">
                      {txn.id} · {formatDateTime(txn.date)}
                    </p>
                  </div>
                  <p className="font-display text-base font-semibold text-ink">
                    {formatCurrency(txn.amount, "USD")}
                  </p>
                </button>
              ))}
            </div>

            <p className="mb-3 mt-6 font-mono text-xs uppercase tracking-wide text-ink-faint">
              2. Reason for dispute
            </p>
            <div className="flex flex-wrap gap-2">
              {reasons.map((r) => (
                <button
                  key={r}
                  onClick={() => setReason(r)}
                  className={`focus-ring rounded-full border px-3 py-1.5 text-xs font-medium transition-colors ${
                    reason === r
                      ? "border-navy bg-navy text-white"
                      : "border-hairline text-ink-soft hover:border-ink-faint"
                  }`}
                >
                  {r}
                </button>
              ))}
            </div>

            <Button className="mt-6" onClick={handleSubmit}>
              Open the negotiation table
            </Button>
          </CardBody>
        </Card>

        <Card className="h-fit">
          <CardBody>
            <p className="font-mono text-xs uppercase tracking-wide text-ink-faint">What happens next</p>
            <ol className="mt-3 space-y-3 text-sm text-ink-soft">
              <li>
                A <span className="font-medium text-ink">timeline</span> is built from this
                transaction automatically.
              </li>
              <li>
                <span className="font-medium text-ink">Merchant</span> is notified and joins the same
                shared table.
              </li>
              <li>
                Both of you see the same evidence, tagged by credibility, as it
                arrives.
              </li>
              <li>
                An <span className="font-medium text-ink">AI recommendation</span> is proposed as
                evidence comes in.
              </li>
            </ol>
          </CardBody>
        </Card>
      </div>
    </AppShell>
  );
}
