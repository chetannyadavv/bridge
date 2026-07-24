import { useState } from "react";
import { useParams } from "react-router-dom";
import { EvidenceCard } from "@/components/dispute/EvidenceCard";
import { Button } from "@/components/ui/Button";
import { useRole } from "@/lib/RoleContext";
import { useDisputes } from "@/lib/DisputeContext";
import type { CredibilityLabel } from "@/types/dispute";
import { UploadCloud } from "lucide-react";

export function SharedEvidenceBoard() {
  const { id } = useParams();
  const { role } = useRole();
  const { getEvidence, addEvidence } = useDisputes();
  const [showForm, setShowForm] = useState(false);
  const [draft, setDraft] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const items = getEvidence(id ?? "");

  async function handleAddEvidence() {
    if (!id || !draft.trim()) return;
    const credibility: CredibilityLabel =
      role === "cardholder" ? "CUSTOMER_STATEMENT" : "MERCHANT_STATEMENT";

    setIsSubmitting(true);
    try {
      await addEvidence(id, {
        uploader: role,
        type: "TEXT",
        credibility,
        summary: draft.trim(),
      });
      setDraft("");
      setShowForm(false);
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleContest(evidenceId: string) {
    // Placeholder only — corresponds to Module 11: Evidence Contest Module (stretch).
    console.log("contest evidence (mock, no backend):", evidenceId);
  }

  return (
    <div>
      <div className="mb-5 rounded-md border border-hairline bg-paper px-3 py-2.5 text-xs text-ink-soft">
        {items.length === 0
          ? "No evidence has been added yet."
          : `${items.length} item${items.length === 1 ? "" : "s"} on the board — visible to both parties.`}
      </div>

      <div className="mb-4 flex items-center justify-between">
        <p className="font-mono text-xs uppercase tracking-wide text-ink-faint">
          Shared board · both parties see identical evidence
        </p>
        <Button size="sm" variant="secondary" onClick={() => setShowForm((v) => !v)}>
          <UploadCloud size={14} className="mr-1.5" />
          Add evidence
        </Button>
      </div>

      {showForm && (
        <div className="mb-4 flex items-center gap-2 rounded-md border border-hairline bg-paper-raised p-3">
          <input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder={
              role === "cardholder" ? "Describe what happened…" : "Describe your response…"
            }
            disabled={isSubmitting}
            className="focus-ring flex-1 rounded-md border border-hairline bg-paper px-3 py-2 text-sm text-ink disabled:opacity-60"
          />
          <Button size="sm" onClick={handleAddEvidence} disabled={!draft.trim() || isSubmitting}>
            {isSubmitting ? "Submitting…" : "Submit"}
          </Button>
        </div>
      )}

      {items.length > 0 && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {items.map((item) => (
            <EvidenceCard key={item.id} evidence={item} onContest={handleContest} />
          ))}
        </div>
      )}
    </div>
  );
}
