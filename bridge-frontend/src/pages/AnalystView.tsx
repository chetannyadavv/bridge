import { Link } from "react-router-dom";
import { AppShell, PageHeading } from "@/components/layout/AppShell";
import { Card, CardBody } from "@/components/ui/Card";
import { StatusPill } from "@/components/ui/StatusPill";
import { Button } from "@/components/ui/Button";
import { useRole } from "@/lib/RoleContext";
import { useDisputes } from "@/lib/DisputeContext";
import { mockAnalystStats } from "@/data/mockData";
import { formatCurrency, formatDateTime } from "@/lib/utils";
import { AlertTriangle, Inbox } from "lucide-react";

function StatTile({ label, value }: { label: string; value: string | number }) {
  return (
    <Card>
      <CardBody>
        <p className="font-mono text-[11px] uppercase tracking-wide text-ink-faint">{label}</p>
        <p className="mt-1.5 font-display text-2xl font-semibold text-ink">{value}</p>
      </CardBody>
    </Card>
  );
}

export function AnalystView() {
  const { role } = useRole();
  const { disputes, disputesError, refreshDisputes } = useDisputes();

  const sorted = [...disputes].sort(
    (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
  );

  return (
    <AppShell>
      <PageHeading
        eyebrow={role === "merchant" ? "Module 18 · Merchant Dashboard" : "Module 17 · Dispute History"}
        title={role === "merchant" ? "Merchant dashboard" : "My disputes"}
        description={
          role === "merchant"
            ? "Your incoming dispute queue and incentive-earnings summary."
            : "Every table you've opened, past and active."
        }
      />

      {disputesError && (
        <div className="mb-5 flex items-center gap-3 rounded-md border border-cardholder/30 bg-cardholder-tint/30 px-4 py-3">
          <AlertTriangle size={16} className="shrink-0 text-cardholder" />
          <p className="flex-1 text-sm text-ink">{disputesError}</p>
          <Button variant="secondary" size="sm" onClick={refreshDisputes}>
            Try again
          </Button>
        </div>
      )}

      {role === "merchant" && (
        <div className="mb-8 grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-6">
          <StatTile label="Open" value={mockAnalystStats.openDisputes} />
          <StatTile label="In negotiation" value={mockAnalystStats.inNegotiation} />
          <StatTile label="Resolved this month" value={mockAnalystStats.resolvedThisMonth} />
          <StatTile label="Avg. resolution" value={`${mockAnalystStats.avgResolutionTimeHours}h`} />
          <StatTile label="Incentives earned" value={mockAnalystStats.incentivesEarned} />
          <StatTile label="Trust score" value={mockAnalystStats.trustScore} />
        </div>
      )}

      {sorted.length === 0 && !disputesError ? (
        <Card>
          <CardBody className="flex flex-col items-center gap-2 py-12 text-center">
            <Inbox size={22} className="text-ink-faint" />
            <p className="text-sm font-medium text-ink">No disputes yet</p>
            <p className="max-w-sm text-sm text-ink-faint">
              Once a dispute is opened, it'll show up here.
            </p>
            <Link to="/disputes/new" className="mt-2">
              <Button size="sm">Create a dispute</Button>
            </Link>
          </CardBody>
        </Card>
      ) : (
        <Card>
          <div className="divide-y divide-hairline">
            {sorted.map((dispute) => (
              <Link
                key={dispute.id}
                to={`/disputes/${dispute.id}`}
                className="focus-ring flex items-center justify-between gap-4 px-4 py-3.5 transition-colors hover:bg-black/[0.02]"
              >
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-ink">
                    {dispute.reason} · {role === "merchant" ? dispute.customer.name : dispute.merchant.name}
                  </p>
                  <p className="mt-0.5 font-mono text-[11px] text-ink-faint">
                    {dispute.id} · {formatDateTime(dispute.createdAt)}
                  </p>
                </div>
                <div className="flex shrink-0 items-center gap-3">
                  <p className="font-display text-sm font-semibold text-ink">
                    {formatCurrency(dispute.amount, dispute.currency)}
                  </p>
                  <StatusPill status={dispute.status} />
                </div>
              </Link>
            ))}
          </div>
        </Card>
      )}
    </AppShell>
  );
}
