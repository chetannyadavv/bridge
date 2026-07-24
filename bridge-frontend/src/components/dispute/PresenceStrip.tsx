import { Circle, RotateCw, WifiOff } from "lucide-react";
import type { ConnectionStatus } from "@/services/websocket";
import { cn } from "@/lib/utils";

const roleLabel: Record<string, string> = {
  cardholder: "Cardholder",
  merchant: "Merchant",
  analyst: "Analyst",
};

const statusCopy: Record<ConnectionStatus, string> = {
  open: "Live",
  connecting: "Reconnecting…",
  closed: "Offline — showing last known state",
};

export function PresenceStrip({
  presence,
  connectionStatus,
}: {
  presence: string[];
  connectionStatus: ConnectionStatus;
}) {
  const onlineLabel =
    presence.length === 0
      ? "No one else online yet"
      : presence.map((role) => `${roleLabel[role] ?? role} online`).join(" · ");

  return (
    <div className="flex items-center gap-2 border-b border-hairline bg-navy px-4 py-2 text-white/90">
      {connectionStatus === "open" ? (
        <Circle size={8} className="fill-settlement text-settlement animate-pulse" />
      ) : connectionStatus === "connecting" ? (
        <RotateCw size={12} className="animate-spin text-caution" />
      ) : (
        <WifiOff size={12} className="text-cardholder" />
      )}
      <p className="font-mono text-xs tracking-wide">{onlineLabel}</p>
      <span
        className={cn(
          "ml-auto rounded px-2 py-0.5 font-mono text-[10px]",
          connectionStatus === "open" ? "bg-white/10 text-white/60" : "bg-cardholder/20 text-white/90"
        )}
      >
        {statusCopy[connectionStatus]}
      </span>
    </div>
  );
}
