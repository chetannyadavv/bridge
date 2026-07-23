import { Link } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/Button";
import { Card, CardBody } from "@/components/ui/Card";
import { ScanSearch, MessagesSquare, FileCheck2, Scale, CheckCircle2 } from "lucide-react";
import { mockDisputes } from "@/data/mockData";

const howItWorks = [
  { icon: ScanSearch, name: "Timeline updated", copy: "Built automatically the moment a dispute opens." },
  { icon: FileCheck2, name: "Evidence received", copy: "Every item is tagged by credibility, visible to both sides." },
  { icon: MessagesSquare, name: "Merchant response received", copy: "Both parties see the same board update in real time." },
  { icon: Scale, name: "AI recommendation ready", copy: "A specific settlement is proposed as evidence arrives." },
  { icon: CheckCircle2, name: "Dispute resolved", copy: "Both sides accept and the case closes — in minutes, not weeks." },
];

export function Landing() {
  return (
    <AppShell>
      <section className="grid grid-cols-1 gap-10 py-6 md:grid-cols-[1.1fr_0.9fr] md:items-center">
        <div>
          <p className="mb-4 font-mono text-xs uppercase tracking-wide text-ink-faint">
            A shared table for disputes
          </p>
          <h1 className="font-display text-5xl font-semibold leading-[1.05] text-ink">
            Two sides.
            <br />
            One ledger.
            <br />
            <span className="text-settlement">No black box.</span>
          </h1>
          <p className="mt-5 max-w-md text-base leading-relaxed text-ink-soft">
            Bridge puts the cardholder and the merchant at the same evidence
            board, in real time, with clear case status and an AI-backed
            recommendation — instead of a claim form and a three-week silence.
          </p>
          <div className="mt-7 flex gap-3">
            <Link to="/disputes/new">
              <Button size="md">Start a dispute</Button>
            </Link>
            <Link to={`/disputes/${mockDisputes[0].id}`}>
              <Button size="md" variant="secondary">
                View a live workspace
              </Button>
            </Link>
          </div>
        </div>

        {/* Signature element: the bridge — two ledger sides meeting at a
            settlement seam. This motif is reused in the Workspace. */}
        <div className="relative overflow-hidden rounded-[var(--radius-card)] border border-hairline bg-paper-raised">
          <div className="grid grid-cols-2">
            <div className="border-r border-hairline bg-cardholder-tint/40 p-5">
              <p className="font-mono text-[11px] uppercase tracking-wide text-cardholder">Cardholder</p>
              <p className="mt-2 text-sm text-ink-soft">"Room didn't match the listing."</p>
            </div>
            <div className="bg-merchant-tint/40 p-5">
              <p className="font-mono text-[11px] uppercase tracking-wide text-merchant">Merchant</p>
              <p className="mt-2 text-sm text-ink-soft">"Check-in confirmed, GPS-verified."</p>
            </div>
          </div>
          <div className="relative flex items-center justify-center border-t border-hairline bg-settlement-tint py-5">
            <div className="absolute left-1/2 top-0 h-full w-px -translate-x-1/2 bg-settlement/30" />
            <div className="text-center">
              <p className="font-mono text-[11px] uppercase tracking-wide text-settlement">
                AI recommends
              </p>
              <p className="mt-1 font-display text-2xl font-semibold text-settlement">
                Partial refund — 50%
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="mt-16">
        <h2 className="font-display text-xl font-semibold text-ink">How Bridge works</h2>
        <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
          {howItWorks.map((step) => (
            <Card key={step.name}>
              <CardBody>
                <step.icon size={18} className="text-navy" />
                <p className="mt-3 font-display text-sm font-semibold text-ink">{step.name}</p>
                <p className="mt-1 text-xs leading-relaxed text-ink-soft">{step.copy}</p>
              </CardBody>
            </Card>
          ))}
        </div>
      </section>
    </AppShell>
  );
}
