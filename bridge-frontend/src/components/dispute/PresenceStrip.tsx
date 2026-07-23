import { Circle } from "lucide-react";

export function PresenceStrip({ message }: { message: string }) {
  return (
    <div className="flex items-center gap-2 border-b border-hairline bg-navy px-4 py-2 text-white/90">
      <Circle size={8} className="fill-settlement text-settlement animate-pulse" />
      <p className="font-mono text-xs tracking-wide">{message}</p>
      <span className="ml-auto rounded bg-white/10 px-2 py-0.5 font-mono text-[10px] text-white/60">
        mock presence · no live socket
      </span>
    </div>
  );
}
