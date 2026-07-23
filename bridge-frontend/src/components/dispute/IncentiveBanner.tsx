import type { IncentiveOffer } from "@/types/dispute";
import { formatRelativeWindow } from "@/lib/utils";
import { Sparkles } from "lucide-react";

export function IncentiveBanner({ incentive }: { incentive: IncentiveOffer }) {
  if (!incentive.active) return null;

  return (
    <div className="flex items-center gap-3 rounded-md border border-settlement/30 bg-settlement-tint px-3.5 py-3">
      <Sparkles size={16} className="shrink-0 text-settlement" />
      <div className="min-w-0">
        <p className="text-sm font-medium text-settlement">{incentive.description}</p>
        <p className="font-mono text-[11px] text-settlement/70">
          {formatRelativeWindow(incentive.windowEndsAt)}
        </p>
      </div>
    </div>
  );
}
