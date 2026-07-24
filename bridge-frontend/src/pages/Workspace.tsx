import { useEffect, useState } from "react";
import { Outlet, useNavigate, useParams, Link } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import { WorkspaceTabs } from "@/components/layout/WorkspaceTabs";
import { PresenceStrip } from "@/components/dispute/PresenceStrip";
import { CaseStatusPanel } from "@/components/dispute/CaseStatusPanel";
import { StatusPill } from "@/components/ui/StatusPill";
import { Button } from "@/components/ui/Button";
import { useRole } from "@/lib/RoleContext";
import { useDisputes } from "@/lib/DisputeContext";
import { formatCurrency } from "@/lib/utils";

export function Workspace() {
  const { id } = useParams();
  const { role } = useRole();
  const navigate = useNavigate();
  const { getDispute, getCaseStatus, getPresence, getConnectionStatus, loadDispute, subscribeToDispute } =
    useDisputes();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    setIsLoading(true);
    loadDispute(id).finally(() => setIsLoading(false));
  }, [id, loadDispute]);

  // Opens a live connection for this dispute+role while the Workspace is
  // mounted, and tears it down on unmount or when id/role changes —
  // switching roles via the header toggle correctly rejoins the room
  // under the new role, updating presence.
  useEffect(() => {
    if (!id) return;
    return subscribeToDispute(id, role);
  }, [id, role, subscribeToDispute]);

  const dispute = getDispute(id ?? "");

  if (isLoading) {
    return (
      <AppShell>
        <p className="text-sm text-ink-faint">Loading dispute…</p>
      </AppShell>
    );
  }

  if (!dispute) {
    return (
      <AppShell>
        <div className="rounded-[var(--radius-card)] border border-hairline bg-paper-raised p-8 text-center">
          <p className="font-display text-lg font-semibold text-ink">Dispute not found</p>
          <p className="mt-1 text-sm text-ink-soft">
            This dispute doesn't exist — it may have been created in a different
            session, or the link is out of date.
          </p>
          <Link to="/analyst" className="mt-4 inline-block">
            <Button variant="secondary" size="sm">
              Back to dashboard
            </Button>
          </Link>
        </div>
      </AppShell>
    );
  }

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
            View resolution
          </Button>
        </div>
      </div>

      <div className="rounded-[var(--radius-card)] border border-hairline bg-paper-raised">
        <PresenceStrip
          presence={getPresence(dispute.id)}
          connectionStatus={getConnectionStatus(dispute.id)}
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
            <CaseStatusPanel steps={getCaseStatus(dispute.id)} />
          </aside>
        </div>
      </div>
    </AppShell>
  );
}
