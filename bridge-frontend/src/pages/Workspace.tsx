import { Outlet, useNavigate, useParams } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import { WorkspaceTabs } from "@/components/layout/WorkspaceTabs";
import { PresenceStrip } from "@/components/dispute/PresenceStrip";
import { CaseStatusPanel } from "@/components/dispute/CaseStatusPanel";
import { StatusPill } from "@/components/ui/StatusPill";
import { Button } from "@/components/ui/Button";
import { useRole } from "@/lib/RoleContext";
import { mockDisputes, mockCaseStatus } from "@/data/mockData";
import { formatCurrency } from "@/lib/utils";

export function Workspace() {
  const { id } = useParams();
  const { role } = useRole();
  const navigate = useNavigate();

  const dispute = mockDisputes.find((d) => d.id === id) ?? mockDisputes[0];
  const counterparty = role === "cardholder" ? dispute.merchant : dispute.customer;

  return (
    <AppShell>
      <div className="mb-5 flex items-start justify-between gap-4">
        <div>
          <p className="mb-1.5 font-mono text-xs uppercase tracking-wide text-ink-faint">
            Module 3 · Negotiation Table &middot; dispute {dispute.id}
          </p>
          <h1 className="font-display text-2xl font-semibold text-ink">
            {dispute.reason} — {formatCurrency(dispute.amount, dispute.currency)}
          </h1>
          <p className="mt-1 text-sm text-ink-soft">
            You're viewing as <span className="font-medium text-ink">{role}</span>, negotiating with{" "}
            {counterparty.name}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <StatusPill status={dispute.status} />
          <Button variant="secondary" size="sm" onClick={() => navigate(`/disputes/${dispute.id}/resolution`)}>
            View resolution (demo)
          </Button>
        </div>
      </div>

      <div className="rounded-[var(--radius-card)] border border-hairline bg-paper-raised">
        <PresenceStrip
          message={
            role === "cardholder"
              ? "Merchant is reviewing evidence…"
              : "Cardholder is reviewing evidence…"
          }
        />

        <div className="grid grid-cols-1 gap-0 lg:grid-cols-[1fr_240px]">
          <div className="border-hairline p-5 lg:border-r">
            <WorkspaceTabs />
            <Outlet />
          </div>

          <aside className="p-5">
            <p className="mb-3 font-mono text-xs uppercase tracking-wide text-ink-faint">
              Case status
            </p>
            <CaseStatusPanel steps={mockCaseStatus} />
          </aside>
        </div>
      </div>
    </AppShell>
  );
}
