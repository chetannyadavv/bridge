import { api } from "@/services/api";
import type { TimelineEvent } from "@/types/dispute";

export interface TimelineEventDto {
  id: string;
  dispute_id: string;
  timestamp: string;
  title: string;
  description: string;
}

export function adaptTimelineEvent(dto: TimelineEventDto): TimelineEvent {
  return {
    id: dto.id,
    disputeId: dto.dispute_id,
    timestamp: dto.timestamp,
    title: dto.title,
    description: dto.description,
  };
}

export async function listTimeline(disputeId: string): Promise<TimelineEvent[]> {
  const dtos = await api.get<TimelineEventDto[]>(`/disputes/${disputeId}/timeline`);
  return dtos.map(adaptTimelineEvent);
}
