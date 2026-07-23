import { RouterProvider } from "react-router-dom";
import { RoleProvider } from "@/lib/RoleContext";
import { router } from "@/router";

export default function App() {
  return (
    <RoleProvider>
      <RouterProvider router={router} />
    </RoleProvider>
  );
}
