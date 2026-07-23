import type { TimelineEvent } from "@/types/dispute";
import { formatDateTime } from "@/lib/utils";

export function TimelineRail({ events }: { events: TimelineEvent[] }) {
  return (
    <ol className="relative ml-3 border-l border-hairline pl-6">
      {events.map((event) => (
        <li key={event.id} className="mb-6 last:mb-0">
          <span className="absolute -ml-[31px] mt-1.5 h-2.5 w-2.5 rounded-full border-2 border-paper-raised bg-navy" />
          <p className="font-mono text-[11px] text-ink-faint">{formatDateTime(event.timestamp)}</p>
          <p className="mt-0.5 font-display text-base font-medium text-ink">{event.title}</p>
          <p className="mt-0.5 text-sm text-ink-soft">{event.description}</p>
        </li>
      ))}
    </ol>
  );
}
