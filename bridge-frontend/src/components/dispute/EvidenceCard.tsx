import type { EvidenceItem } from "@/types/dispute";
import { CredibilityTag } from "./CredibilityTag";
import { formatDateTime, cn } from "@/lib/utils";
import { Image, FileText, MessageCircle, Database, Flag } from "lucide-react";

const typeIcon = {
  IMAGE: Image,
  PDF: FileText,
  TEXT: MessageCircle,
  SYSTEM_RECORD: Database,
} as const;

const sourceStyles = {
  cardholder: "border-l-cardholder",
  merchant: "border-l-merchant",
  system: "border-l-ink-faint",
} as const;

export function EvidenceCard({
  evidence,
  onContest,
}: {
  evidence: EvidenceItem;
  onContest?: (id: string) => void;
}) {
  const Icon = typeIcon[evidence.type];

  return (
    <div
      className={cn(
        "rounded-[var(--radius-card)] border border-hairline border-l-4 bg-paper-raised p-3",
        sourceStyles[evidence.uploader]
      )}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start gap-2">
          <div className="mt-0.5 rounded bg-black/[0.04] p-1.5 text-ink-soft">
            <Icon size={14} />
          </div>
          <div>
            <p className="text-sm leading-snug text-ink">{evidence.summary}</p>
            <p className="mt-1 font-mono text-[11px] text-ink-faint">
              {evidence.uploader === "system" ? "System record" : evidence.uploader === "cardholder" ? "Submitted by cardholder" : "Submitted by merchant"}
              {" · "}
              {formatDateTime(evidence.createdAt)}
            </p>
          </div>
        </div>
        {onContest && (
          <button
            onClick={() => onContest(evidence.id)}
            title="Contest this evidence (stretch goal — placeholder)"
            className="focus-ring rounded p-1 text-ink-faint hover:text-caution"
          >
            <Flag size={14} />
          </button>
        )}
      </div>
      <div className="mt-2.5">
        <CredibilityTag credibility={evidence.credibility} />
      </div>
    </div>
  );
}
