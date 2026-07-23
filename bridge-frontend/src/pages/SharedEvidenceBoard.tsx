import { useState } from "react";
import { useParams } from "react-router-dom";
import { EvidenceCard } from "@/components/dispute/EvidenceCard";
import { useRole } from "@/lib/RoleContext";
import { mockEvidence } from "@/data/mockData";
import { Button } from "@/components/ui/Button";
import { UploadCloud } from "lucide-react";

export function SharedEvidenceBoard() {
  const { id } = useParams();
  const { role } = useRole();
  const [items] = useState(mockEvidence.filter((e) => e.disputeId === id || true));

  const statusCopy =
    role === "cardholder"
      ? "New evidence has been added. Merchant response received — a GPS-confirmed check-in log is now on the board."
      : "Merchant response received. New evidence has been added — a room photo is now on the board.";

  function handleContest(evidenceId: string) {
    // Placeholder only — corresponds to Module 11: Evidence Contest Module (stretch).
    console.log("contest evidence (mock, no backend):", evidenceId);
  }

  return (
    <div>
      <div className="mb-5 rounded-md border border-hairline bg-paper px-3 py-2.5 text-xs text-ink-soft">
        {statusCopy}
      </div>

      <div className="mb-4 flex items-center justify-between">
        <p className="font-mono text-xs uppercase tracking-wide text-ink-faint">
          Shared board · both parties see identical evidence
        </p>
        <Button size="sm" variant="secondary">
          <UploadCloud size={14} className="mr-1.5" />
          Add evidence
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {items.map((item) => (
          <EvidenceCard key={item.id} evidence={item} onContest={handleContest} />
        ))}
      </div>
    </div>
  );
}
