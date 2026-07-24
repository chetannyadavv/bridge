import { Link } from "react-router-dom";
import { AppShell, PageHeading } from "@/components/layout/AppShell";
import { Card, CardBody } from "@/components/ui/Card";
import { StatusPill } from "@/components/ui/StatusPill";
import { useRole } from "@/lib/RoleContext";
import { useDisputes } from "@/lib/DisputeContext";
import { mockAnalystStats } from "@/data/mockData";
import { formatCurrency, formatDateTime } from "@/lib/utils";

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
  const { disputes } = useDisputes();

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
    </AppShell>
  );
}
