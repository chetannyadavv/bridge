import { api } from "@/services/api";
import type { EvidenceItem, EvidenceType, CredibilityLabel, Role } from "@/types/dispute";

export interface EvidenceDto {
  id: string;
  dispute_id: string;
  uploader: Role | "system";
  type: EvidenceType;
  credibility: CredibilityLabel;
  summary: string;
  file_path: string | null;
  created_at: string;
}

export interface AddEvidenceInput {
  uploader: Role;
  type: EvidenceType;
  credibility: CredibilityLabel;
  summary: string;
  filePath?: string;
}

export function adaptEvidence(dto: EvidenceDto): EvidenceItem {
  return {
    id: dto.id,
    disputeId: dto.dispute_id,
    uploader: dto.uploader,
    type: dto.type,
    credibility: dto.credibility,
    summary: dto.summary,
    filePath: dto.file_path ?? undefined,
    createdAt: dto.created_at,
  };
}

export async function listEvidence(disputeId: string): Promise<EvidenceItem[]> {
  const dtos = await api.get<EvidenceDto[]>(`/disputes/${disputeId}/evidence`);
  return dtos.map(adaptEvidence);
}

export async function addEvidence(disputeId: string, input: AddEvidenceInput): Promise<EvidenceItem> {
  const dto = await api.post<EvidenceDto>(`/disputes/${disputeId}/evidence`, {
    uploader: input.uploader,
    type: input.type,
    credibility: input.credibility,
    summary: input.summary,
    file_path: input.filePath ?? null,
  });
  return adaptEvidence(dto);
}
