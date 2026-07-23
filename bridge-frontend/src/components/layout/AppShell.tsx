import type { ReactNode } from "react";
import { Header } from "./Header";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-paper">
      <Header />
      <main className="mx-auto max-w-[1200px] px-6 py-8">{children}</main>
    </div>
  );
}

export function PageHeading({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="mb-6 flex items-start justify-between gap-4">
      <div>
        {eyebrow && (
          <p className="mb-1.5 font-mono text-xs uppercase tracking-wide text-ink-faint">
            {eyebrow}
          </p>
        )}
        <h1 className="font-display text-3xl font-semibold text-ink">{title}</h1>
        {description && <p className="mt-1.5 max-w-2xl text-sm text-ink-soft">{description}</p>}
      </div>
      {action}
    </div>
  );
}
