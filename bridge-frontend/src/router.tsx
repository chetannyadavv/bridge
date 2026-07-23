import { createBrowserRouter } from "react-router-dom";
import { Landing } from "@/pages/Landing";
import { CreateDispute } from "@/pages/CreateDispute";
import { Workspace } from "@/pages/Workspace";
import { Timeline } from "@/pages/Timeline";
import { SharedEvidenceBoard } from "@/pages/SharedEvidenceBoard";
import { SettlementPanel } from "@/pages/SettlementPanel";
import { Resolution } from "@/pages/Resolution";
import { AnalystView } from "@/pages/AnalystView";

export const router = createBrowserRouter([
  { path: "/", element: <Landing /> },
  { path: "/disputes/new", element: <CreateDispute /> },
  {
    path: "/disputes/:id",
    element: <Workspace />,
    children: [
      { index: true, element: <Timeline /> },
      { path: "evidence", element: <SharedEvidenceBoard /> },
      { path: "settlement", element: <SettlementPanel /> },
    ],
  },
  { path: "/disputes/:id/resolution", element: <Resolution /> },
  { path: "/analyst", element: <AnalystView /> },
]);
