# Bridge — Frontend Skeleton

A React + Vite + TypeScript frontend skeleton for the Negotiation Table
product, built against **Architecture v1.1 (FINAL)**.

This is UI structure and mock data only. There is **no backend logic, no
AI Orchestrator calls, no authentication, and no WebSocket connections**
implemented here — those are separate modules per the frozen functional
decomposition.

## Getting started

```bash
npm install
npm run dev       # local dev server
npm run build     # production build (already verified clean)
npm run preview   # preview the production build
```

## Stack

React 19 + TypeScript + Vite, Tailwind CSS v4 (via `@tailwindcss/vite`,
no separate config file — theme tokens live in `src/index.css`),
`react-router-dom` for routing, `lucide-react` for icons. No `shadcn/ui`
CLI components were generated; a small set of hand-built primitives in
`src/components/ui` fill the same role to keep the skeleton dependency-light.

## Design system

Token system and rationale documented at the top of `src/index.css`.
Short version: a "ledger" aesthetic — cool paper background, ink navy
structure, a warm cardholder-side color and a cool merchant-side color
that meet at a single settlement-green seam. Fraunces (display serif) +
IBM Plex Sans (body) + IBM Plex Mono (data/tags, evoking a ledger).

## Pages → routes → functional modules

| Page | Route | Corresponds to |
|---|---|---|
| Landing | `/` | — (marketing/entry only) |
| Create Dispute | `/disputes/new` | Module 1 — Dispute Intake |
| Workspace | `/disputes/:id` | Module 3 layout — Negotiation Table shell (tabs + agent rail) |
| Timeline | `/disputes/:id` (index) | Module 3 — Dispute Timeline Generator (first view on entry) |
| Shared Evidence Board | `/disputes/:id/evidence` | Modules 2, 4, 5, 6, 7 — Evidence Collector, Credibility Tagging, Manual Submission, Advocates |
| Settlement Panel | `/disputes/:id/settlement` | Modules 8, 9, 10, 14 — Settlement Mediator, Recommendation Panel, Explanation Generator, Incentive |
| Resolution | `/disputes/:id/resolution` | Modules 15, 16 — Resolution & Acceptance, Resolution Display |
| Analyst View | `/analyst` | Modules 17, 18 — Dispute History (cardholder) / Merchant Dashboard (merchant) |

The Workspace page is a route layout (`<Outlet />`) so Timeline, Shared
Evidence Board, and Settlement Panel share one persistent shell —
presence strip, agent activity rail, and tab navigation — matching the
product spec's single shared session per dispute.

## Mock-only concerns, explicitly marked in code

- `src/lib/RoleContext.tsx` — a demo-only cardholder/merchant view
  switcher in the header. This is **not** authentication; it exists so
  the mirrored-view product requirement can be demoed statically.
- `src/data/mockData.ts` — all disputes, evidence, timeline events,
  settlement history, agent activity, and incentive data. Shapes mirror
  Architecture v1.1 §6 (Database) so swapping in real API calls later
  should not require type changes.
- `PresenceStrip` and `AgentBadge` render static/mock states and are
  visually labeled as such — no live socket is implied.
- Buttons that map to stretch-goal modules (Counter-Offer, Evidence
  Contest) are present but disabled/inert, so the full page structure
  is visible without implying functionality that isn't built yet.

## Not implemented (by design, per this task's scope)

- Backend/API calls, AI Orchestrator, database
- Authentication (Mock JWT)
- WebSocket events (`dispute_created`, `evidence_added`, etc.)
- File upload handling
- Counter-offer and evidence-contest flows (stretch goals, UI stubs only)
