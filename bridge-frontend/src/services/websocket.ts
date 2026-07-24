// Sprint 4: the only file that touches the native WebSocket API. UI
// components never import this directly — they go through
// DisputeContext's `subscribeToDispute`, which owns one DisputeSocket
// per actively-viewed dispute. See DisputeContext.tsx.

export type DisputeSocketEventType =
  | "dispute_updated"
  | "evidence_updated"
  | "timeline_updated"
  | "recommendation_updated"
  | "presence_updated";

export interface DisputeSocketMessage<T = unknown> {
  type: DisputeSocketEventType;
  payload: T;
}

export type ConnectionStatus = "connecting" | "open" | "closed";

interface DisputeSocketHandlers {
  onMessage: (message: DisputeSocketMessage) => void;
  onStatusChange?: (status: ConnectionStatus) => void;
}

const WS_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000").replace(
  /^http/,
  "ws"
);

const BASE_RECONNECT_DELAY_MS = 1000;
const MAX_RECONNECT_DELAY_MS = 8000;

/**
 * One DisputeSocket per (dispute, role) the app is actively viewing.
 * Push-only from the server's side — this sprint has no client -> server
 * message protocol (no chat, no typing indicators). Reconnects
 * automatically with capped exponential backoff on any disconnect that
 * wasn't explicitly requested via close().
 */
export class DisputeSocket {
  private readonly disputeId: string;
  private readonly role: string;
  private readonly handlers: DisputeSocketHandlers;
  private socket: WebSocket | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private reconnectAttempts = 0;
  private closedByClient = false;

  constructor(disputeId: string, role: string, handlers: DisputeSocketHandlers) {
    this.disputeId = disputeId;
    this.role = role;
    this.handlers = handlers;
    this.open();
  }

  private open() {
    this.handlers.onStatusChange?.("connecting");
    const url = `${WS_BASE_URL}/ws/disputes/${this.disputeId}?role=${encodeURIComponent(this.role)}`;
    const socket = new WebSocket(url);
    this.socket = socket;

    socket.onopen = () => {
      this.reconnectAttempts = 0;
      this.handlers.onStatusChange?.("open");
    };

    socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as DisputeSocketMessage;
        this.handlers.onMessage(message);
      } catch {
        // Malformed message from the wire — nothing to recover, just
        // drop it. There's no client-side message protocol to validate
        // against beyond "is this valid JSON".
      }
    };

    socket.onclose = () => {
      this.handlers.onStatusChange?.("closed");
      if (!this.closedByClient) this.scheduleReconnect();
    };

    socket.onerror = () => {
      socket.close();
    };
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) return;
    const delay = Math.min(
      BASE_RECONNECT_DELAY_MS * 2 ** this.reconnectAttempts,
      MAX_RECONNECT_DELAY_MS
    );
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.reconnectAttempts += 1;
      if (!this.closedByClient) this.open();
    }, delay);
  }

  /** Explicit teardown — stops reconnect attempts and closes the socket. */
  close() {
    this.closedByClient = true;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.socket?.close();
  }
}
