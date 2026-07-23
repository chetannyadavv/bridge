import { NavLink } from "react-router-dom";
import { useRole } from "@/lib/RoleContext";
import { cn } from "@/lib/utils";
import { GitBranch } from "lucide-react";

const navItems = [
  { to: "/", label: "Home", end: true },
  { to: "/disputes/new", label: "Create Dispute" },
  { to: `/disputes/dsp_8841`, label: "Workspace" },
  { to: "/analyst", label: "Analyst View" },
];

export function Header() {
  const { role, setRole } = useRole();

  return (
    <header className="sticky top-0 z-20 border-b border-hairline bg-navy text-white">
      <div className="mx-auto flex h-14 max-w-[1200px] items-center gap-6 px-6">
        <NavLink to="/" className="flex items-center gap-2 font-display text-lg font-semibold">
          <GitBranch size={18} className="text-settlement" />
          Bridge
        </NavLink>

        <nav className="flex items-center gap-1">
          {navItems.map((item) => (
            <NavLink
              key={item.label}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                cn(
                  "focus-ring rounded-md px-3 py-1.5 text-sm font-medium text-white/70 transition-colors hover:text-white",
                  isActive && "bg-white/10 text-white"
                )
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="ml-auto flex items-center gap-2">
          <span className="font-mono text-[11px] text-white/50">viewing as</span>
          <div className="flex rounded-md border border-white/15 p-0.5">
            <button
              onClick={() => setRole("cardholder")}
              className={cn(
                "focus-ring rounded px-2.5 py-1 text-xs font-medium transition-colors",
                role === "cardholder" ? "bg-cardholder text-white" : "text-white/60 hover:text-white"
              )}
            >
              Cardholder
            </button>
            <button
              onClick={() => setRole("merchant")}
              className={cn(
                "focus-ring rounded px-2.5 py-1 text-xs font-medium transition-colors",
                role === "merchant" ? "bg-merchant text-white" : "text-white/60 hover:text-white"
              )}
            >
              Merchant
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
