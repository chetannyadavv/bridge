import type { CredibilityLabel } from "@/types/dispute";
import { cn } from "@/lib/utils";
import { ShieldCheck, MapPin, Receipt, MessageSquare, HelpCircle } from "lucide-react";

const config: Record<
  CredibilityLabel,
  { label: string; icon: typeof ShieldCheck; className: string }
> = {
  VERIFIED_TRANSACTION: {
    label: "Verified Transaction",
    icon: ShieldCheck,
    className: "bg-settlement-tint text-settlement",
  },
  GPS_CONFIRMED: {
    label: "GPS Confirmed",
    icon: MapPin,
    className: "bg-settlement-tint text-settlement",
  },
  TIMESTAMPED_RECEIPT: {
    label: "Timestamped Receipt",
    icon: Receipt,
    className: "bg-merchant-tint text-merchant",
  },
  CUSTOMER_STATEMENT: {
    label: "Customer Statement",
    icon: MessageSquare,
    className: "bg-cardholder-tint text-cardholder",
  },
  MERCHANT_STATEMENT: {
    label: "Merchant Statement",
    icon: MessageSquare,
    className: "bg-merchant-tint text-merchant",
  },
  UNVERIFIED: {
    label: "Unverified",
    icon: HelpCircle,
    className: "bg-caution-tint text-[#7A5A1E]",
  },
};

export function CredibilityTag({ credibility }: { credibility: CredibilityLabel }) {
  const { label, icon: Icon, className } = config[credibility];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2 py-1 text-[11px] font-mono font-medium tracking-wide",
        className
      )}
    >
      <Icon size={12} strokeWidth={2.25} />
      {label}
    </span>
  );
}
