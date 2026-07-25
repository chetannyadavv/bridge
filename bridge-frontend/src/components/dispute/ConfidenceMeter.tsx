import { cn } from "@/lib/utils";

export function ConfidenceMeter({ confidence }: { confidence: number }) {
  const barColor =
    confidence >= 70 ? "bg-settlement" : confidence >= 40 ? "bg-caution" : "bg-cardholder";
  const textColor =
    confidence >= 70 ? "text-settlement" : confidence >= 40 ? "text-[#7A5A1E]" : "text-cardholder";

  return (
    <div className="flex items-center gap-2.5">
      <div className="h-1.5 w-28 overflow-hidden rounded-full bg-black/[0.08]">
        <div
          className={cn("h-full rounded-full transition-[width]", barColor)}
          style={{ width: `${Math.max(0, Math.min(100, confidence))}%` }}
        />
      </div>
      <span className={cn("font-mono text-xs font-medium", textColor)}>{confidence}% confidence</span>
    </div>
  );
}
