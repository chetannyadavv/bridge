import type { DisputeStatus } from "@/types/dispute";
import { cn } from "@/lib/utils";

const statusStyles: Record<DisputeStatus, string> = {
  OPEN: "bg-caution-tint text-[#7A5A1E]",
  IN_NEGOTIATION: "bg-merchant-tint text-merchant",
  RESOLVED: "bg-settlement-tint text-settlement",
  CLOSED: "bg-black/[0.06] text-ink-faint",
};

const statusLabels: Record<DisputeStatus, string> = {
  OPEN: "Open",
  IN_NEGOTIATION: "In negotiation",
  RESOLVED: "Resolved",
  CLOSED: "Closed",
};

export function StatusPill({ status }: { status: DisputeStatus }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium font-mono tracking-wide",
        statusStyles[status]
      )}
    >
      {statusLabels[status]}
    </span>
  );
}
