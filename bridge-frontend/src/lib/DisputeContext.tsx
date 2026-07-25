import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import type {
  Dispute,
  EvidenceItem,
  TimelineEvent,
  SettlementRecord,
  CaseStatusStep,
  CaseStatusState,
  Role,
  CredibilityLabel,
  EvidenceType,
} from "@/types/dispute";
import * as disputesService from "@/services/disputes";
import * as evidenceService from "@/services/evidence";
import * as timelineService from "@/services/timeline";
import * as recommendationsService from "@/services/recommendations";
import { DisputeSocket, type ConnectionStatus, type DisputeSocketMessage } from "@/services/websocket";

// ---------------------------------------------------------------------------
// Sprint 3: this store's public shape (getDispute, getEvidence, getTimeline,
// getSettlementHistory, getLatestSettlement, getCaseStatus, createDispute,
// addEvidence, acceptSettlement) is unchanged from Sprint 2's in-memory
// version — only the implementation moved from a seeded reducer to real
// fetches against the FastAPI backend via src/services/*.
//
// Sprint 4 adds `subscribeToDispute(id, role)`, `getPresence(id)`, and
// `getConnectionStatus(id)`. Live updates (evidence/timeline/recommendation/
// dispute status changes pushed over the websocket) land in the exact same
// state maps that REST-driven reads already use — so getEvidence/getTimeline/
// getCaseStatus etc. automatically reflect realtime pushes with zero changes
// to those functions or to any page that only reads through them.
//
// mutating REST calls (createDispute/addEvidence/acceptSettlement) still
// force-refetch via loadDispute afterward, same as Sprint 3 — this is
// intentionally redundant with the websocket broadcast the mutating client
// will also receive: it guarantees the client sees its own change even if
// its own websocket connection happens to be down (Requirement 7 — REST
// must keep working standalone).
// ---------------------------------------------------------------------------

interface AddEvidenceInput {
  uploader: Role;
  type: EvidenceType;
  credibility: CredibilityLabel;
  summary: string;
}

interface CreateDisputeInput {
  transactionId: string;
  merchantName: string;
  reason: string;
  amount: number;
  currency?: string;
}

interface DisputeContextValue {
  disputes: Dispute[];
  disputesError: string | null;
  refreshDisputes: () => Promise<void>;
  getDispute: (id: string) => Dispute | undefined;
  getEvidence: (id: string) => EvidenceItem[];
  getTimeline: (id: string) => TimelineEvent[];
  getSettlementHistory: (id: string) => SettlementRecord[];
  getLatestSettlement: (id: string) => SettlementRecord | undefined;
  getCaseStatus: (id: string) => CaseStatusStep[];
  getPresence: (id: string) => string[];
  getConnectionStatus: (id: string) => ConnectionStatus;
  loadDispute: (id: string, opts?: { force?: boolean }) => Promise<void>;
  subscribeToDispute: (id: string, role: string) => () => void;
  createDispute: (input: CreateDisputeInput) => Promise<string>;
  addEvidence: (disputeId: string, input: AddEvidenceInput) => Promise<void>;
  acceptSettlement: (disputeId: string, role: Role) => Promise<void>;
}

const DisputeContext = createContext<DisputeContextValue | undefined>(undefined);

export function DisputeProvider({ children }: { children: ReactNode }) {
  const [disputes, setDisputes] = useState<Record<string, Dispute>>({});
  const [disputeList, setDisputeList] = useState<Dispute[]>([]);
  const [disputesError, setDisputesError] = useState<string | null>(null);
  const [evidence, setEvidence] = useState<Record<string, EvidenceItem[]>>({});
  const [timeline, setTimeline] = useState<Record<string, TimelineEvent[]>>({});
  const [settlement, setSettlement] = useState<Record<string, SettlementRecord[]>>({});
  const [presence, setPresence] = useState<Record<string, string[]>>({});
  const [connectionStatus, setConnectionStatus] = useState<Record<string, ConnectionStatus>>({});
  const loadedIds = useRef<Set<string>>(new Set());
  const sockets = useRef<Record<string, DisputeSocket>>({});

  // Sprint 6 robustness: the dispute list fetch previously had no error
  // handling at all — if the backend was unreachable, this silently
  // failed and the list just stayed empty forever, with no indication
  // to the user that anything had gone wrong.
  const refreshDisputes = useCallback(async () => {
    try {
      const list = await disputesService.listDisputes();
      setDisputesError(null);
      setDisputeList(list);
      setDisputes((prev) => {
        const next = { ...prev };
        list.forEach((d) => {
          next[d.id] = d;
        });
        return next;
      });
    } catch {
      setDisputesError("Couldn't reach the server. Check your connection and try again.");
    }
  }, []);

  useEffect(() => {
    refreshDisputes();
  }, [refreshDisputes]);

  const getDispute = useCallback((id: string) => disputes[id], [disputes]);
  const getEvidence = useCallback((id: string) => evidence[id] ?? [], [evidence]);
  const getTimeline = useCallback(
    (id: string) =>
      [...(timeline[id] ?? [])].sort(
        (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
      ),
    [timeline]
  );
  const getSettlementHistory = useCallback((id: string) => settlement[id] ?? [], [settlement]);
  const getLatestSettlement = useCallback(
    (id: string) => {
      const history = getSettlementHistory(id);
      return history[history.length - 1];
    },
    [getSettlementHistory]
  );
  const getPresence = useCallback((id: string) => presence[id] ?? [], [presence]);
  const getConnectionStatus = useCallback(
    (id: string): ConnectionStatus => connectionStatus[id] ?? "connecting",
    [connectionStatus]
  );

  const getCaseStatus = useCallback(
    (id: string): CaseStatusStep[] => {
      const dispute = getDispute(id);
      const evidenceList = getEvidence(id);
      const settlementHistory = getSettlementHistory(id);
      const hasEvidence = evidenceList.length > 0;
      const hasMerchantEvidence = evidenceList.some((e) => e.uploader === "merchant");
      const hasRecommendation = settlementHistory.length > 0;
      const resolved = dispute?.status === "RESOLVED" || dispute?.status === "CLOSED";

      const evidenceState: CaseStatusState = hasEvidence ? "complete" : "pending";
      const merchantState: CaseStatusState = hasMerchantEvidence
        ? "complete"
        : hasEvidence
          ? "in_progress"
          : "pending";
      const recommendationState: CaseStatusState = resolved
        ? "complete"
        : hasRecommendation
          ? "in_progress"
          : "pending";
      const resolvedState: CaseStatusState = resolved ? "complete" : "pending";

      return [
        { id: "cs_1", label: "Dispute Created", state: "complete", timestamp: dispute?.createdAt },
        {
          id: "cs_2",
          label: "Evidence Received",
          state: evidenceState,
          timestamp: hasEvidence ? evidenceList[evidenceList.length - 1].createdAt : undefined,
        },
        {
          id: "cs_3",
          label: "Merchant Response Received",
          state: merchantState,
          timestamp: hasMerchantEvidence
            ? evidenceList.find((e) => e.uploader === "merchant")?.createdAt
            : undefined,
        },
        {
          id: "cs_4",
          label: "Recommendation Pending",
          state: recommendationState,
          timestamp: hasRecommendation ? getLatestSettlement(id)?.updatedAt : undefined,
        },
        {
          id: "cs_5",
          label: "Dispute Resolved",
          state: resolvedState,
          timestamp: resolved ? getLatestSettlement(id)?.updatedAt : undefined,
        },
      ];
      // Case status is entirely derived from state already kept fresh by
      // both REST loads and websocket pushes — no dedicated
      // "case_status_updated" event exists or is needed (Requirement 4).
    },
    [getDispute, getEvidence, getSettlementHistory, getLatestSettlement]
  );

  const loadDispute = useCallback(async (id: string, opts?: { force?: boolean }) => {
    if (!opts?.force && loadedIds.current.has(id)) return;

    const [dispute, evidenceItems, timelineItems, settlementItems] = await Promise.all([
      disputesService.getDispute(id),
      evidenceService.listEvidence(id),
      timelineService.listTimeline(id),
      recommendationsService.listRecommendations(id),
    ]);

    setDisputes((prev) => ({ ...prev, [id]: dispute }));
    setEvidence((prev) => ({ ...prev, [id]: evidenceItems }));
    setTimeline((prev) => ({ ...prev, [id]: timelineItems }));
    setSettlement((prev) => ({ ...prev, [id]: settlementItems }));
    loadedIds.current.add(id);
  }, []);

  // Opens (or reuses) a live websocket connection for a dispute+role and
  // wires its push messages directly into the same state maps REST reads
  // use. Returns an unsubscribe function — callers (Workspace) tear this
  // down in a useEffect cleanup on unmount or when id/role changes, which
  // is also how switching the role toggle correctly rejoins the room
  // under the new role (old presence entry leaves, new one joins).
  const subscribeToDispute = useCallback((id: string, role: string): (() => void) => {
    if (sockets.current[id]) {
      // Already subscribed (e.g. a duplicate effect firing in dev
      // StrictMode) — don't open a second connection.
      return () => {};
    }

    const socket = new DisputeSocket(id, role, {
      onStatusChange: (status) => {
        setConnectionStatus((prev) => ({ ...prev, [id]: status }));
      },
      onMessage: (message: DisputeSocketMessage) => {
        switch (message.type) {
          case "dispute_updated": {
            const dto = message.payload as disputesService.DisputeDto;
            setDisputes((prev) => ({ ...prev, [id]: disputesService.adaptDispute(dto) }));
            break;
          }
          case "evidence_updated": {
            const dtos = message.payload as evidenceService.EvidenceDto[];
            setEvidence((prev) => ({ ...prev, [id]: dtos.map(evidenceService.adaptEvidence) }));
            break;
          }
          case "timeline_updated": {
            const dtos = message.payload as timelineService.TimelineEventDto[];
            setTimeline((prev) => ({ ...prev, [id]: dtos.map(timelineService.adaptTimelineEvent) }));
            break;
          }
          case "recommendation_updated": {
            const dtos = message.payload as recommendationsService.RecommendationDto[];
            setSettlement((prev) => ({
              ...prev,
              [id]: dtos.map(recommendationsService.adaptRecommendation),
            }));
            break;
          }
          case "presence_updated": {
            const payload = message.payload as { roles: string[] };
            setPresence((prev) => ({ ...prev, [id]: payload.roles }));
            break;
          }
        }
      },
    });

    sockets.current[id] = socket;
    loadedIds.current.add(id); // the socket's initial push is a full load too

    return () => {
      socket.close();
      delete sockets.current[id];
    };
  }, []);

  const createDispute = useCallback(
    async (input: CreateDisputeInput): Promise<string> => {
      const dispute = await disputesService.createDispute(input);
      setDisputes((prev) => ({ ...prev, [dispute.id]: dispute }));
      setDisputeList((prev) => [dispute, ...prev]);
      await loadDispute(dispute.id, { force: true });
      return dispute.id;
    },
    [loadDispute]
  );

  const addEvidence = useCallback(
    async (disputeId: string, input: AddEvidenceInput) => {
      await evidenceService.addEvidence(disputeId, {
        uploader: input.uploader,
        type: input.type,
        credibility: input.credibility,
        summary: input.summary,
      });
      await loadDispute(disputeId, { force: true });
    },
    [loadDispute]
  );

  const acceptSettlement = useCallback(
    async (disputeId: string, role: Role) => {
      await recommendationsService.acceptRecommendation(disputeId, role);
      await loadDispute(disputeId, { force: true });
    },
    [loadDispute]
  );

  const value = useMemo<DisputeContextValue>(
    () => ({
      disputes: disputeList,
      disputesError,
      refreshDisputes,
      getDispute,
      getEvidence,
      getTimeline,
      getSettlementHistory,
      getLatestSettlement,
      getCaseStatus,
      getPresence,
      getConnectionStatus,
      loadDispute,
      subscribeToDispute,
      createDispute,
      addEvidence,
      acceptSettlement,
    }),
    [
      disputeList,
      disputesError,
      refreshDisputes,
      getDispute,
      getEvidence,
      getTimeline,
      getSettlementHistory,
      getLatestSettlement,
      getCaseStatus,
      getPresence,
      getConnectionStatus,
      loadDispute,
      subscribeToDispute,
      createDispute,
      addEvidence,
      acceptSettlement,
    ]
  );

  return <DisputeContext.Provider value={value}>{children}</DisputeContext.Provider>;
}

export function useDisputes() {
  const ctx = useContext(DisputeContext);
  if (!ctx) throw new Error("useDisputes must be used within a DisputeProvider");
  return ctx;
}
