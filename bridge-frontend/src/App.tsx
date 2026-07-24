import { RouterProvider } from "react-router-dom";
import { RoleProvider } from "@/lib/RoleContext";
import { DisputeProvider } from "@/lib/DisputeContext";
import { router } from "@/router";

export default function App() {
  return (
    <RoleProvider>
      <DisputeProvider>
        <RouterProvider router={router} />
      </DisputeProvider>
    </RoleProvider>
  );
}
