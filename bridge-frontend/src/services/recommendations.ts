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
  reason_code?: string | null;
  category?: string | null;
  engine_recommendation?: string | null;
  confidence?: number | null;
  summary?: string | null;
  reasons?: string[];
  missing_evidence?: string[];
  next_steps?: string[];
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
    reasonCode: dto.reason_code ?? undefined,
    category: dto.category ?? undefined,
    engineRecommendation: dto.engine_recommendation ?? undefined,
    confidence: dto.confidence ?? undefined,
    summary: dto.summary ?? undefined,
    reasons: dto.reasons ?? [],
    missingEvidence: dto.missing_evidence ?? [],
    nextSteps: dto.next_steps ?? [],
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
