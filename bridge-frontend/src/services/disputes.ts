import { api } from "@/services/api";
import type { Dispute, DisputeStatus, Party } from "@/types/dispute";

// Backend response shape (snake_case, flat party names, Decimal-as-string
// amount) — kept separate from the frontend's Dispute type so the rest of
// the app never has to know the wire format.
export interface DisputeDto {
  id: string;
  transaction_id: string;
  customer_name: string;
  merchant_name: string;
  reason: string;
  amount: string;
  currency: string;
  status: DisputeStatus;
  created_at: string;
}

export interface CreateDisputeInput {
  transactionId: string;
  merchantName: string;
  amount: number;
  currency?: string;
  reason: string;
}

function toParty(name: string, role: Party["role"]): Party {
  // The backend has no separate parties table (no auth in this sprint) —
  // synthesize a stable-enough id from the name for the frontend's Party
  // shape rather than changing that type.
  return { id: `${role}_${name.toLowerCase().replace(/\s+/g, "_")}`, name, role };
}

export function adaptDispute(dto: DisputeDto): Dispute {
  return {
    id: dto.id,
    transactionId: dto.transaction_id,
    merchant: toParty(dto.merchant_name, "merchant"),
    customer: toParty(dto.customer_name, "cardholder"),
    status: dto.status,
    reason: dto.reason,
    amount: Number(dto.amount),
    currency: dto.currency,
    createdAt: dto.created_at,
  };
}

export async function listDisputes(): Promise<Dispute[]> {
  const dtos = await api.get<DisputeDto[]>("/disputes");
  return dtos.map(adaptDispute);
}

export async function getDispute(id: string): Promise<Dispute> {
  const dto = await api.get<DisputeDto>(`/disputes/${id}`);
  return adaptDispute(dto);
}

export async function createDispute(input: CreateDisputeInput): Promise<Dispute> {
  const dto = await api.post<DisputeDto>("/disputes", {
    transaction_id: input.transactionId,
    merchant_name: input.merchantName,
    amount: input.amount,
    currency: input.currency ?? "USD",
    reason: input.reason,
  });
  return adaptDispute(dto);
}
