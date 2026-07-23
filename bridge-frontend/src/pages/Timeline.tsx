import { useParams, Link } from "react-router-dom";
import { TimelineRail } from "@/components/dispute/TimelineRail";
import { mockTimeline } from "@/data/mockData";
import { CheckCircle2 } from "lucide-react";

export function Timeline() {
  const { id } = useParams();
  const events = mockTimeline.filter((e) => e.disputeId === id);

  return (
    <div>
      <div className="mb-5 flex items-center gap-2 rounded-md border border-hairline bg-paper px-3 py-2.5 text-xs text-ink-soft">
        <CheckCircle2 size={14} className="text-settlement" />
        Timeline updated automatically — this is the first thing both parties
        see when the case opens.
      </div>

      <TimelineRail events={events.length ? events : mockTimeline} />

      <Link
        to={`/disputes/${id}/evidence`}
        className="focus-ring mt-6 inline-block text-sm font-medium text-navy underline underline-offset-2"
      >
        Continue to the evidence board →
      </Link>
    </div>
  );
}
