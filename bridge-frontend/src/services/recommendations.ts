import { api } from "@/services/api";
import type { SettlementRecord, SettlementRecommendationType, Role } from "@/types/dispute";

export interface RecommendationDto {
  id: string;
  dispute_id: string;
  recommendation: SettlementRecommendationType;
  percentage: number | null;
  reason: string;
  explanation: string;
  accepted_by: string[];
  updated_at: string;
}

export function adaptRecommendation(dto: RecommendationDto): SettlementRecord {
  return {
    id: dto.id,
    disputeId: dto.dispute_id,
    recommendation: dto.recommendation,
    percentage: dto.percentage,
    reason: dto.reason,
    explanation: dto.explanation,
    acceptedBy: dto.accepted_by.length > 0 ? (dto.accepted_by as Role[]) : null,
    updatedAt: dto.updated_at,
  };
}

export async function listRecommendations(disputeId: string): Promise<SettlementRecord[]> {
  const dtos = await api.get<RecommendationDto[]>(`/disputes/${disputeId}/recommendation`);
  return dtos.map(adaptRecommendation);
}

export async function acceptRecommendation(disputeId: string, role: Role): Promise<SettlementRecord> {
  const dto = await api.post<RecommendationDto>(`/disputes/${disputeId}/recommendation/accept`, { role });
  return adaptRecommendation(dto);
}
