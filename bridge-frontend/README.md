# Bridge — Frontend

A React + Vite + TypeScript frontend for the Negotiation Table product,
built against **Architecture v1.1 (FINAL)**.

As of Sprint 4, this talks to a real backend (`bridge-backend/`, FastAPI +
PostgreSQL) instead of seeded mock state — creating a dispute, adding
evidence, and accepting a settlement all persist server-side now.
Realtime updates arrive over a WebSocket connection (one per viewed
dispute). There is still **no AI and no authentication**.

## Getting started

The backend must be running first — see `bridge-backend/README.md`
(quickest path: `docker compose up --build` from the `bridge/` root).

```bash
npm install
cp .env.example .env   # defaults to http://localhost:8001, edit if needed
npm run dev             # local dev server
npm run build            # production build (verified clean)
npm run preview           # preview the production build
npm run lint               # oxlint
```

## Stack

React 19 + TypeScript + Vite, Tailwind CSS v4 (via `@tailwindcss/vite`,
no separate config file — theme tokens live in `src/index.css`),
`react-router-dom` for routing, `lucide-react` for icons. No `shadcn/ui`
CLI components were generated; a small set of hand-built primitives in
`src/components/ui` fill the same role to keep the app dependency-light.
No new libraries were introduced in Sprint 3 — no Redux, MobX, Zustand,
or React Query. Data fetching and caching use plain `useState` /
`useCallback` / `useRef` inside `DisputeContext`, matching the existing
`RoleContext` pattern.

## Design system

Token system and rationale documented at the top of `src/index.css`.
Short version: a "ledger" aesthetic — cool paper background, ink navy
structure, a warm cardholder-side color and a cool merchant-side color
that meet at a single settlement-green seam. Fraunces (display serif) +
IBM Plex Sans (body) + IBM Plex Mono (data/tags, evoking a ledger).

**Sprint 3 made no visual or structural changes** — same pages, same
layout, same components. The only user-visible differences are: data
persists across reloads now, and there's a brief loading state when
opening a dispute (previously seeded state was available instantly).

## Pages → routes → functional modules

| Page | Route | Corresponds to |
|---|---|---|
| Landing | `/` | — (marketing/entry only) |
| Create Dispute | `/disputes/new` | Module 1 — Dispute Intake |
| Workspace | `/disputes/:id` | Module 3 layout — Negotiation Table shell (tabs + case status rail) |
| Timeline | `/disputes/:id` (index) | Module 3 — Dispute Timeline Generator (first view on entry) |
| Shared Evidence Board | `/disputes/:id/evidence` | Modules 2, 4, 5, 6, 7 — Evidence Collector, Credibility Tagging, Manual Submission, Advocates |
| Settlement Panel | `/disputes/:id/settlement` | Modules 8, 9, 10, 14 — Settlement Mediator, Recommendation Panel, Explanation Generator, Incentive |
| Resolution | `/disputes/:id/resolution` | Modules 15, 16 — Resolution & Acceptance, Resolution Display |
| Analyst View | `/analyst` | Modules 17, 18 — Dispute History (cardholder) / Merchant Dashboard (merchant) |

## Services layer (Sprint 3)

`src/services/` is the only place `fetch()` is called from. Components
never call `fetch` directly — they go through `DisputeContext`, which
goes through these:

- **`api.ts`** — base client (`api.get` / `api.post`), reads
  `VITE_API_BASE_URL`, throws `ApiError` on non-2xx responses.
- **`disputes.ts`** — `listDisputes`, `getDispute`, `createDispute`.
- **`evidence.ts`** — `listEvidence`, `addEvidence`.
- **`timeline.ts`** — `listTimeline`.
- **`recommendations.ts`** — `listRecommendations`, `acceptRecommendation`.

Each service module adapts the backend's snake_case DTOs (e.g.
`transaction_id`, `Decimal`-as-string `amount`) to the existing frontend
types in `src/types/dispute.ts` — those types were **not** changed for
Sprint 3, so nothing downstream of `DisputeContext` needed to change its
data shapes.

## State layer

`src/lib/DisputeContext.tsx` keeps the exact same public API it had in
Sprint 2 (`getDispute`, `getEvidence`, `getTimeline`,
`getSettlementHistory`, `getLatestSettlement`, `getCaseStatus`,
`createDispute`, `addEvidence`, `acceptSettlement`) — only the
implementation changed, from a `useReducer` over seeded mock arrays to
real fetches against the backend. One addition: `loadDispute(id)`, called
by `Workspace` and `Resolution` to trigger the initial fetch for a given
dispute, since data no longer exists locally until something asks for it.

`createDispute`, `addEvidence`, and `acceptSettlement` are now `async` —
callers `await` them and handle the loading/error state locally (see
`CreateDispute.tsx`, `SharedEvidenceBoard.tsx`, `SettlementPanel.tsx` for
the small `isSubmitting` / try-catch additions this required).

**Pages that only *read* from the context — `Timeline.tsx`, and the read
paths in `SharedEvidenceBoard.tsx` and `SettlementPanel.tsx` — needed no
changes at all**, since the context's read functions kept the same
signatures.

## Realtime (Sprint 4)

`src/services/websocket.ts` exports `DisputeSocket` — the only file in
the app that touches the native `WebSocket` API, per this sprint's
requirement. It auto-reconnects with capped exponential backoff (1s,
2s, 4s, 8s cap) on any connection drop that wasn't explicitly requested.

`DisputeContext.subscribeToDispute(id, role)` owns one `DisputeSocket`
per actively-viewed dispute and routes every incoming message into the
**same state maps** REST reads already populate (`getEvidence`,
`getTimeline`, `getSettlementHistory`, etc.) — so those functions, and
anything derived from them like `getCaseStatus`, automatically reflect
live pushes with no changes of their own. `Workspace.tsx` calls
`subscribeToDispute` in a `useEffect` keyed on `[id, role]`, so switching
the role toggle correctly leaves and rejoins the dispute's room under
the new role.

Two new context reads power the presence strip:
- `getPresence(id)` — the list of currently connected roles for a dispute.
- `getConnectionStatus(id)` — `"connecting" | "open" | "closed"`, driving
  the live/reconnecting/offline indicator in `PresenceStrip.tsx`.

**REST remains fully independent of the socket.** `createDispute`,
`addEvidence`, and `acceptSettlement` all still make their REST call and
then force-refetch via `loadDispute`, exactly as in Sprint 3 — this is
intentional redundancy with the websocket broadcast the same client will
also receive, so the app keeps working even if realtime is completely
unavailable (Requirement 7 / Acceptance Test 7).

## Mock-only concerns, explicitly marked in code

- `src/lib/RoleContext.tsx` — a demo-only cardholder/merchant view
  switcher in the header. This is **not** authentication; it exists so
  the mirrored-view product requirement can be demoed statically.
- `src/data/mockData.ts` — trimmed to `mockIncentive` and
  `mockAnalystStats`. Everything else (disputes, evidence, timeline,
  settlement history) is backend-owned.
- The "Add evidence" flow on the Shared Evidence Board is a single text
  field, not a file uploader — there is no file storage in this sprint.
- Buttons that map to stretch-goal modules (Counter-Offer, Evidence
  Contest) are present but disabled/inert.

## Not implemented (by design, per this task's scope)

- AI / OpenAI API calls
- Authentication (Mock JWT), login
- WebSocket rooms (implemented in Sprint 4)
- Background workers, Redis, Celery, caching
