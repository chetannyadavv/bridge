import type { CaseStatusStep } from "@/types/dispute";
import { cn, formatDateTime } from "@/lib/utils";
import { Check, Circle, Loader2 } from "lucide-react";

const stateStyles = {
  complete: "text-settlement bg-settlement-tint",
  in_progress: "text-merchant bg-merchant-tint",
  pending: "text-ink-faint bg-black/[0.03]",
} as const;

function StepIcon({ state }: { state: CaseStatusStep["state"] }) {
  if (state === "complete") return <Check size={13} />;
  if (state === "in_progress") return <Loader2 size={13} className="animate-spin" />;
  return <Circle size={13} />;
}

export function CaseStatusPanel({ steps }: { steps: CaseStatusStep[] }) {
  return (
    <div className="space-y-2">
      {steps.map((step) => (
        <div
          key={step.id}
          className="flex items-center gap-2 rounded-md border border-hairline bg-paper-raised px-2.5 py-2"
        >
          <div className={cn("rounded p-1.5", stateStyles[step.state])}>
            <StepIcon state={step.state} />
          </div>
          <div className="min-w-0">
            <p className="truncate text-xs font-medium text-ink">{step.label}</p>
            <p className={cn("font-mono text-[10px]", stateStyles[step.state].split(" ")[0])}>
              {step.state === "complete" && step.timestamp
                ? formatDateTime(step.timestamp)
                : step.state === "in_progress"
                  ? "In progress"
                  : "Pending"}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
