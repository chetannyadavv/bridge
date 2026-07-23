import { NavLink, useParams } from "react-router-dom";
import { cn } from "@/lib/utils";

const tabs = [
  { segment: "", label: "Timeline" },
  { segment: "evidence", label: "Evidence Board" },
  { segment: "settlement", label: "Settlement" },
];

export function WorkspaceTabs() {
  const { id } = useParams();
  const base = `/disputes/${id}`;

  return (
    <div className="mb-5 flex gap-1 border-b border-hairline">
      {tabs.map((tab) => (
        <NavLink
          key={tab.label}
          to={tab.segment ? `${base}/${tab.segment}` : base}
          end
          className={({ isActive }) =>
            cn(
              "focus-ring -mb-px border-b-2 border-transparent px-3 py-2.5 text-sm font-medium text-ink-soft transition-colors hover:text-ink",
              isActive && "border-navy text-ink"
            )
          }
        >
          {tab.label}
        </NavLink>
      ))}
    </div>
  );
}
