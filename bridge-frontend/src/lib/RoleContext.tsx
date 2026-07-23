import { createContext, useContext, useState, type ReactNode } from "react";
import type { Role } from "@/types/dispute";

interface RoleContextValue {
  role: Role;
  setRole: (role: Role) => void;
}

const RoleContext = createContext<RoleContextValue | undefined>(undefined);

// NOTE: this is a demo-only view switcher, not authentication.
// Architecture v1.1 specifies Mock JWT auth as a separate concern —
// this context exists purely so the skeleton can render the mirrored
// cardholder / merchant views described in the product spec.
export function RoleProvider({ children }: { children: ReactNode }) {
  const [role, setRole] = useState<Role>("cardholder");
  return <RoleContext.Provider value={{ role, setRole }}>{children}</RoleContext.Provider>;
}

export function useRole() {
  const ctx = useContext(RoleContext);
  if (!ctx) throw new Error("useRole must be used within a RoleProvider");
  return ctx;
}
