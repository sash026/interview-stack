# InterviewStack — Session Handoff

_Generated as a handoff snapshot so a fresh session can resume without losing context. Delete this file once its contents are stale._

## 1. Current Project Status

InterviewStack is a customer-interview intelligence platform. By the end of Day 3 the backend was complete and verified end-to-end: upload → async transcription (Celery) → AI insight extraction (structured pain points/sentiment/competitors/etc., provider-abstracted) → pgvector embeddings → semantic search. That work is committed and pushed to `main` on `github.com/sash026/interview-stack`.

**Today (Day 4)** the objective was to build the product/UX layer on top: a dashboard, analytics/trends, an interview explorer with filters, a polished detail page, semantic search UI, and CSV export. Backend additions for this are done and verified. Frontend is partially done:

- ✅ Dashboard (`/`) — fully built, verified in browser with real seeded data, looks correct.
- 🔶 Interview Explorer (`/interviews`) — page/components built, **but there is an active, unresolved bug**: the filter form's Apply button does not actually pass the selected filter values through to the API call (see Blockers below). This was mid-investigation when the session was interrupted.
- ⬜ Interview Detail page (`/interviews/[id]`) — not started (Day 3 built a minimal status-polling view at a different route shape; this still needs the full "polished" version the Day 4 spec asks for: header, transcript viewer, insight sections, similar interviews).
- ⬜ Trends page (`/trends`) — not started.
- ⬜ Semantic Search page (`/search`) — not started (backend already supports it fully).
- ⬜ Final end-to-end browser verification pass — not started.

**Nothing from today's session is committed to git yet.** The working tree is dirty (see `git status` output in Context Snippets). Do not lose this before committing.

All local dev services are currently running (see Context Snippets for exact commands/ports): Postgres 18 + pgvector, Redis, FastAPI (`uvicorn --reload`), Celery worker, Next.js dev server. The DB is seeded with 22 realistic demo interviews (19 completed + 3 in-flight in various states) via `backend/scripts/seed_demo_data.py`.

## 2. Changes Made This Session

### Backend (all verified with `ruff check` + `mypy`, both clean; live-curled against seeded data)

- **`backend/app/services/interview_service.py`** (modified) — added `list_interviews(db, *, page, page_size, status, sentiment, pain_point_category, customer_type, date_from, date_to, q)` returning `(items, total)`. Joins `Insight`/`PainPoint` only when a filter needs them; `q` is a simple title `ILIKE`.
- **`backend/app/schemas/interview.py`** (modified) — added `InterviewListItemResponse` (id, title, status, input_type, created_at, sentiment, customer_type, summary_preview, pain_point_categories, **competitors** — added later for CSV export) and `InterviewListResponse` (items, total, page, page_size, total_pages).
- **`backend/app/api/v1/routers/interviews.py`** (modified) — added `GET /interviews` (list, paginated/filterable) with a `_to_list_item()` mapper. Existing routes (`/upload`, `/{id}`, `/{id}/status`, `/{id}/retry`, `/{id}/similar`) untouched.
- **`backend/app/schemas/analytics.py`** (new) — `PainPointCount`, `CompetitorCount`, `SentimentCount`, `RecentInterviewItem`, `DashboardMetricsResponse`, `PainPointTrendPoint`, `SentimentTrendPoint`, `CategoryBreakdownItem`, `TrendsResponse`.
- **`backend/app/services/analytics_service.py`** (new) — `get_dashboard_metrics(db, ...)` (total completed count, top pain points, sentiment breakdown w/ %, top competitors, recent interviews) and `get_trends(db, days=30)` (day-bucketed pain point trend, sentiment trend, full category breakdown). Competitor counting uses one raw parameterized SQL query (`jsonb_array_elements_text` + `CROSS JOIN LATERAL`) because it doesn't map cleanly onto the ORM query builder — documented inline why.
- **`backend/app/api/v1/routers/dashboard.py`** (new) — `GET /dashboard/metrics`.
- **`backend/app/api/v1/routers/analytics.py`** (new) — `GET /analytics/trends?days=`.
- **`backend/app/main.py`** (modified) — registered the two new routers.
- **`backend/scripts/seed_demo_data.py`** (new) — one-off dev seed script, NOT part of the app package. Inserts 19 realistic, varied completed interviews (varied sentiment/pain-point categories/competitors/customer types/dates over ~43 days) plus 3 in-flight ones (processing/uploaded/failed) directly via the real SQLAlchemy models, so every dashboard/analytics query is exercised against genuine Postgres rows. **Why this exists**: `MockAIProvider` (used since there's no OpenAI key in this sandbox) always returns identical placeholder insights regardless of input — real chart variety requires either a real LLM or hand-seeded realistic data. Chose the latter since "do not add more AI functionality" was explicit today. Reuses `app.services.ai.mock_provider._deterministic_unit_vector` for embeddings so pgvector cosine-distance queries don't hit a zero-vector.
  - Script refuses to run if the `interviews` table is non-empty (prints a message and exits) — it's a from-scratch seeder, not an upsert.

### Frontend

- **`frontend/package.json`** (modified) — added `recharts`.
- **shadcn additions**: `badge.tsx`, `select.tsx`, `skeleton.tsx`, `separator.tsx`, `tabs.tsx` (tabs installed but not yet used).
- **`frontend/src/lib/taxonomy.ts`** (new) — single source of truth for: pain-point category labels, sentiment labels/hex colors/badge classes, status badge variants, a qualitative chart color palette, and `formatDate()`. Used across dashboard/explorer/detail/trends to avoid drift.
- **`frontend/src/lib/api/dashboard.ts`** (new), **`trends.ts`** (new), **`search.ts`** (new) — typed fetch wrappers matching the new backend schemas exactly.
- **`frontend/src/lib/api/interviews.ts`** (modified) — added `PainPoint`, `Insight` types and `insights` field on `InterviewDetail` (this was missing before today — a real pre-existing gap, the backend already returned it). Added `InterviewListItem`/`InterviewListResponse`/`InterviewListFilters`, `listInterviews()`, `getSimilarInterviews()`. Added `PAIN_POINT_CATEGORIES`/`SENTIMENTS` const arrays (single source of truth, imported by the Zod filter schema).
- **`frontend/src/lib/schemas/interview-filters.ts`** (new) — Zod schema + `EMPTY_FILTERS` default for the Explorer's filter form.
- **Hooks** (new): `use-dashboard-metrics.ts`, `use-trends.ts`, `use-interviews-list.ts` (uses `placeholderData` to avoid pagination flash), `use-semantic-search.ts` (mutation, since it's user-triggered not auto-fetched), `use-similar-interviews.ts`.
- **`frontend/src/components/layout/nav-bar.tsx`** (new) — top nav, active-state via `usePathname`. Wired into `frontend/src/app/layout.tsx` (modified) which now wraps children in a `<main>` with consistent padding/max-width.
- **`frontend/src/app/upload/page.tsx`** (new) — the pre-existing upload form, moved here from `/`.
- **`frontend/src/app/page.tsx`** (modified, rewritten) — now the Dashboard: metric cards (total interviews, top pain point, dominant sentiment), pain point bar chart, sentiment donut chart, competitor list, recent interviews list. Loading (skeletons)/error(retry button)/empty states all present. **Verified working in browser with real data.**
- **Dashboard components** (new, in `components/dashboard/`): `metric-card.tsx`, `pain-point-chart.tsx` (recharts horizontal bar), `sentiment-chart.tsx` (recharts donut + legend grid), `competitor-list.tsx` (bar-list, not a chart lib), `recent-interviews.tsx`.
- **`frontend/src/app/interviews/page.tsx`** (new) — Explorer page: filter form, paginated card grid, prev/next pagination, CSV export button, loading/error/empty states. **Has the active bug — see Blockers.**
- **`frontend/src/components/interviews/interview-card.tsx`** (new), **`interview-filters.tsx`** (new, RHF + Zod, shadcn `Select` via `Controller` since Radix Select isn't a native form element).
- **`frontend/src/components/export/export-csv-button.tsx`** (new) — loops through all matching pages (respecting backend's page_size≤100 cap) and generates/downloads a CSV client-side (no new backend endpoint needed).

### Bug fixes found and fixed along the way (not part of the original ask, but real defects)

- **`frontend/src/app/globals.css`** (modified) — **pre-existing site-wide font bug**: the shadcn-generated `@theme inline` block had `--font-sans: var(--font-sans);` (self-referential/circular — presumably a mismatch from whatever font-variable-name convention the shadcn "nova" preset assumed vs. what `next/font` was actually configured to emit, `--font-geist-sans`). This silently made the **entire app** render in the browser's default serif fallback (`Times`) since Day 1 — nobody had visually inspected typography closely until today. Root-caused via `getComputedStyle` + fetching the compiled CSS directly (see investigation trail in conversation history if needed). Fix: bypassed the `@theme` layer entirely and set `html { font-family: var(--font-geist-sans), ui-sans-serif, system-ui, sans-serif; }` directly in the `@layer base` block — confirmed working via `getComputedStyle(document.documentElement).fontFamily`.

## 3. System Architecture & Decisions

- **"Customer name" = `Interview.title`.** There is no separate customer-name field in the schema; the upload form's title field has always doubled as this (e.g. "Acme Corp - Quarterly Review"). Deliberately did NOT add a new field/migration for this — flagged as an assumption, not silently done.
- **Demo data is seeded via a script that uses real models**, not hardcoded frontend mock data. This was a deliberate choice to keep "no fake data" honest: the charts only ever render what a real aggregation query returns from real Postgres rows; only the *seed content* is invented, same as any app's demo/seed data.
- **New backend endpoints were added only where nothing existing could serve the UI**: `GET /interviews` (list — didn't exist before today), `GET /dashboard/metrics`, `GET /analytics/trends`. CSV export deliberately got **no** new endpoint — it reuses `GET /interviews` in a loop and generates the CSV client-side, per "only add endpoints if existing APIs cannot support the UI."
- **Competitors aggregation uses raw SQL** (`jsonb_array_elements_text` + `CROSS JOIN LATERAL`, parameterized, in `analytics_service.py`) rather than fighting SQLAlchemy's table-valued-function API, which is a known rough edge. Everything else uses the ORM.
- **RHF + Zod is used for both the Explorer filter form and (planned, not yet built) the Search input**, matching the existing upload-form pattern rather than ad hoc `useState` per field.
- **Filters/pagination live in local component state** (`useState` in `app/interviews/page.tsx`), not the URL — a deliberate scope cut for time (a "real" product would put this in `useSearchParams`/URL for shareable/bookmarkable filtered views). Server data itself stays in TanStack Query; only the "what filters are currently selected" UI state is local, which is appropriate (it's not a copy of server data).
- **Charts use recharts directly** (not shadcn's `chart.tsx` wrapper) with a small hand-picked color palette in `lib/taxonomy.ts` (`CHART_PALETTE`, `SENTIMENT_HEX`) — chosen for simplicity/reliability over fighting recharts' loose TypeScript types further than necessary. Colors are plain hex strings, not Tailwind classes, passed directly to recharts' `fill`/`stroke` props.
- **pgvector semantic search ranking is only "plumbing-correct," not semantically meaningful**, since `AI_PROVIDER=mock` uses a hash-derived deterministic vector, not real embeddings. This is a known, previously-flagged limitation, not new.

## 4. Blockers & Remaining Tasks

### ✅ RESOLVED (investigated fresh session, 2026-07-07) — Interview Explorer filter bug does NOT reproduce

Picked this up as the first item this session. Added a defensive `onInvalid` handler to `handleSubmit` in `interview-filters.tsx` (harmless, kept — logs `console.error("Filter form validation failed:", errors)` on the rare case validation fails), then did extensive live verification against `/tmp/backend_dev.log` and React internals (walked the fiber tree to read react-hook-form's actual `getValues()` state directly).

**Finding**: the filter → Apply → API chain works correctly end-to-end. Verified: sentiment filter (`sentiment=negative` reached the backend, results correctly narrowed to 7 Negative interviews), pain_point_category filter, Reset, and Next/Previous pagination (`page=2` reached the backend correctly) — all confirmed via direct backend log tail plus a browser screenshot.

**Why it looked broken before**: the `preview_click` browser-automation tool fires a synthetic mousedown+mouseup for Radix `Select` components essentially instantaneously (same tick), which races Radix's dismissable-layer logic and causes the dropdown to open-then-immediately-close on a single "click" — so an option never actually gets selected via that tool. Confirmed this is a tooling artifact, not a real regression: dispatching pointerdown/pointerup with a realistic ~80ms gap (mimicking real mouse timing) opens the Select correctly and selection persists reliably. A real user's mouse click behaves like the 80ms-gap case, not the CDP-instantaneous case. No product code was at fault; **no logic fix was needed**.

Only real code change from this investigation: the added `onInvalid` logger in `interview-filters.tsx` (kept, since it's good defensive practice for the future and does not change behavior on valid submissions).

**Note for future browser-automation testing on this repo**: don't trust a single `preview_click` on a Radix `Select` trigger/item — it can silently no-op. Prefer dispatching `pointerdown`→(small delay)→`pointerup`+`click` via `preview_eval`, or click, then re-check `data-state`/re-click if it shows `"closed"` unexpectedly.

### ✅ Task #11 — Interview Detail page (done, 2026-07-07)

Built fresh rather than extending Day 3's minimal `components/interview-status.tsx` (that component is untouched and still used only by the upload-flow polling view at `components/interview-upload-form.tsx`; kept as-is, out of scope to touch).

New files:
- `frontend/src/app/interviews/[id]/page.tsx` — async server component (Next.js 16 requires `params` to be awaited: `const { id } = await params`), delegates to the client view.
- `frontend/src/components/interviews/interview-detail-view.tsx` — the actual page. Reuses `useInterview`/`useRetryInterview` (already had polling + retry built in from Day 3) and `useSimilarInterviews` (only called when `status === "completed"`, since the backend 409s on `/similar` for non-completed interviews — no hook change needed, just gated at the call site). Layout: header (title, input_type icon, date, status badge) → uploaded/processing spinner card, or failed card with reason + retry, or (completed) a 2-col grid: left = Tabs("Overview" insight sections / "Transcript"), right = metadata card (sentiment, customer_type) + Similar Interviews list linking to their own detail pages. Verified in-browser against real seeded data for all four statuses (completed/failed/processing/uploaded has no seed row but shares the same code path as processing), dark mode, and mobile width. `tsc --noEmit` and `eslint` both clean across the whole frontend.

**Browser-automation note (same root cause as the Explorer finding above)**: Radix `Tabs` triggers have the identical issue as `Select` — `preview_click` and plain `.click()` don't register on the first try; only dispatching `pointerdown` → ~80ms delay → `pointerup`+`click` switches tabs reliably. Not a product bug, just confirms the earlier finding generalizes to other Radix components in this stack. Use the same realistic-timing dispatch pattern for any future Radix-component testing on this repo.

### ✅ Task #12 — Trends page (done, 2026-07-07)

New files:
- `frontend/src/app/trends/page.tsx` — plain client page (no route params, so no async-params concern). Local `useState<number>(30)` for the day-range, fed into the existing `useTrends(days)` hook. Loading/error/retry pattern copied from the Dashboard page for consistency.
- `frontend/src/components/trends/pain-point-trend-chart.tsx`, `sentiment-trend-chart.tsx`, `category-breakdown-chart.tsx`.
- `frontend/src/lib/taxonomy.ts` (modified) — added `CATEGORY_COLOR`, a fixed category→hex mapping derived from `CHART_PALETTE` by iterating `Object.keys(CATEGORY_LABELS)` (12 categories, 12 palette colors, 1:1 by index) so a given pain-point category always renders the same color across the Pain Point Trend chart, the Category Breakdown chart, and (if extended later) anywhere else.

**Design call on chart type**: the seed data is sparse (~19 completed interviews spread over 43 days, mostly 1 pain point each), and the backend returns day-bucketed rows only for days that actually had activity (no zero-filling). A 12-series line chart over that would be unreadable. Used **stacked bar charts** instead for both Pain Point Trend and Sentiment Trend (one bar per date-with-data, segmented by category/sentiment) — reads correctly regardless of how sparse the window is. Category Breakdown reuses the Dashboard's horizontal-bar style but colors each bar by `CATEGORY_COLOR` (via recharts `<Cell>`) rather than a single flat color, since it's showing the full category taxonomy rather than a top-N list.

Verified live: default 30-day view, switching to "Last 7 days" (confirmed correct `?days=7` request and re-rendered chart with narrower data/legend), dark mode (see note below), and mobile width. `tsc --noEmit` and `eslint` both clean across the whole frontend.

**Dark mode testing note**: this app's dark theme is **class-based** (`@custom-variant dark (&:is(.dark *))` in `globals.css`), not automatic via OS/browser `prefers-color-scheme`. `preview_resize`'s `colorScheme` emulation sets the media feature but does **not** add the `.dark` class to `<html>`, so it has no visual effect here — there is currently no theme-toggle UI wired up in the app that would add that class either. To actually preview dark mode in this repo, run `document.documentElement.classList.add('dark')` via `preview_eval` instead of relying on `colorScheme`.

### ⬜ Not started yet (in original task-list order)

### ✅ Task #13 — Semantic Search page (done, 2026-07-07)

New files:
- `frontend/src/app/search/page.tsx` — RHF+Zod search form (`semanticSearchSchema` in new `frontend/src/lib/schemas/semantic-search.ts`, min 2 / max 500 chars) driving `useSemanticSearch()` (a mutation, triggered explicitly on submit — already existed, unchanged). Four states: idle prompt, loading skeletons, error message, and results list (or an explicit "No interviews matched" card for zero results).
- `frontend/src/components/interviews/search-result-card.tsx` — extracted `SearchResultCard({ result })` (title, similarity % badge, summary, links to `/interviews/{id}`). This was pulled out of `interview-detail-view.tsx`'s `SimilarInterviews` section (Task #11) since both places render the exact same `SemanticSearchResult` shape identically — `interview-detail-view.tsx` was updated to import and use the shared component instead of its own inline JSX, no behavior change there.

**Spec-vs-API gap, flagged not silently worked around**: the Day 4 spec asked for the results list to show "similarity score/summary/pain points," but the backend's `SemanticSearchResult` schema (`backend/app/schemas/embedding.py`) only returns `interview_id`, `title`, `summary`, `similarity` — there is no pain-points field on this endpoint, and adding one would mean a backend change, which is out of scope per this task being called out as "purely frontend work." Built against what the API actually returns (similarity + summary); pain points are not shown on search results. If that's wanted, it needs a backend schema/query change first.

Verified live: real search returns ranked results from the seeded interviews (query "customers upset about pricing increases" correctly surfaced the pricing-related interviews at the top), Zod validation (1-char query shows "Enter at least 2 characters" and does not fire a request), dark mode, and mobile width. `tsc --noEmit` and `eslint` clean across the whole frontend. As previously documented, ranking quality itself is limited by `MockAIProvider`'s hash-based embeddings (not semantically meaningful) — known, pre-existing limitation, not something this page can fix.

### ⬜ Not started yet (in original task-list order)

### ✅ Task #14 — Full end-to-end browser verification (done, 2026-07-07)

- `tsc --noEmit` and `eslint` both clean across the whole frontend (final pass, after all four pages).
- **CSV export — actually verified this time**, not just code-reviewed: intercepted `URL.createObjectURL`'s Blob in-browser (via `preview_eval`, since headless Chrome doesn't expose a downloads folder to inspect) and read its contents directly. Confirmed: correct header row, correct CSV escaping (a summary containing a comma was correctly wrapped in quotes), pagination loop correctly walked all pages (22 rows = exact total interview count), correct filename (`interviews-export-<date>.csv`), and — applied the Negative sentiment filter first and re-exported — confirmed the export correctly narrows to the 7 filtered rows rather than always exporting everything.
- **Full real upload smoke test** (not just seeded data): uploaded a brand-new interview via the actual `/upload` form with real text notes. It went through the whole live pipeline (FastAPI → Celery worker → MockAIProvider → pgvector embedding) and completed successfully; verified its detail page rendered correctly (summary, pain points, sentiment, similar-interviews all populated from real DB data) and that it appeared correctly in the Explorer and Dashboard aggregates afterward. **Note**: this added one real row to the dev DB — title "E2E Test Co - Verification Pass", completed, neutral/onboarding. Demo data is now 20 completed / 23 total instead of 19/22. Left in place since it's harmless real data through the real pipeline, not a mock artifact — delete it (`DELETE FROM interviews WHERE title = 'E2E Test Co - Verification Pass';`) if a clean round-number demo count is wanted before a demo.
- Console: no errors on any page. Backend log: no unexpected 5xx across ~800 requests (a few pre-existing 404/409/422 entries found were all from earlier deliberate dev-time edge-case testing, not from today's pages). Celery log: clean.
- Responsive: spot-checked all five pages (Dashboard, Explorer, Detail, Trends, Search) at mobile (375px), tablet (768px), and desktop (1280px) — all correctly reflow using the same `lg:` breakpoint convention used app-wide.
- Cross-page navigation re-verified: Explorer card → Detail page, Detail page's Back link and Similar Interviews links, nav bar across all 5 routes.

**No bugs found in this pass.** Everything built today (Explorer filters, Detail page, Trends, Search, CSV export) works correctly end-to-end against both the seeded demo data and a fresh real upload.

### ⬜ Not started yet

1. **Nothing has been committed or pushed today.** The E2E pass is done and clean — review the full diff, commit (likely 1-2 commits, following this session's established message style — see `git log` for tone), and ask before pushing (this repo's convention all session has been: commit locally, then explicitly ask "want me to push?" before `git push`).

## 5. Context Snippets

### Repo & branches
- Path: `/Users/saisharanbalagopal/Documents/Mac/Comp.Sci/personal/side_projects/interview-stack`
- Remote: `https://github.com/sash026/interview-stack.git`, current branch `main` @ `40f9b83` (nothing today committed on top of this yet)
- Other local-only branches (untouched, safety nets from earlier history-rewrite work, not related to today's feature work): `backup-before-author-fix`, `backup-before-claude-removal`
- Git identity for commits: `sash026 <sharanmtp06@gmail.com>` (both global and local repo config)

### Local dev services (all running right now)
```
Postgres 18 + pgvector:  /opt/homebrew/opt/postgresql@18/bin/pg_ctl -D /opt/homebrew/var/postgresql@18 status
                         → port 5434, db "interview_stack", user postgres/postgres
Redis:                   /opt/homebrew/opt/redis/bin/redis-cli -p 6380 ping   → port 6380
Backend (FastAPI):       uvicorn app.main:app --reload --port 8000  (venv at backend/venv)
                         log: /tmp/backend_dev.log  ← tail this for the cleanest request signal, avoids frontend network-log noise
Celery worker:           celery -A app.core.celery_app.celery_app worker --loglevel=info
                         log: /tmp/celery_worker.log
Frontend (Next.js):      npm run dev, port 3000 (preview tool serverId will differ each session)
```
`backend/.env`: `DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5434/interview_stack`, `CELERY_BROKER_URL`/`CELERY_RESULT_BACKEND=redis://localhost:6380/0`. Frontend has no `.env.local` — relies on the `NEXT_PUBLIC_API_URL ?? "http://localhost:8000"` fallback in `lib/api/*.ts`.

To reseed from scratch: `DELETE FROM interviews;` (cascades to transcripts/insights/pain_points/embeddings) then `cd backend && source venv/bin/activate && python -m scripts.seed_demo_data`.

### API endpoints relevant to today's work
```
GET  /api/v1/interviews?page=&page_size=&status=&sentiment=&pain_point_category=&customer_type=&date_from=&date_to=&q=
     → { items: InterviewListItemResponse[], total, page, page_size, total_pages }
GET  /api/v1/interviews/{id}                  → full detail incl. transcript + insights (unchanged today)
GET  /api/v1/interviews/{id}/similar?limit=   → unchanged today
POST /api/v1/semantic-search                  → unchanged today
GET  /api/v1/dashboard/metrics?top_pain_points_limit=&top_competitors_limit=&recent_limit=
GET  /api/v1/analytics/trends?days=30
```

### Key types/enums (must stay in sync between backend and `lib/api/interviews.ts` / `lib/taxonomy.ts`)
- `InterviewStatus`: uploaded | processing | completed | failed
- `PainPointCategory` (12, fixed taxonomy): pricing, reporting, authentication, onboarding, integrations, performance, ux, documentation, analytics, security, collaboration, support
- `CustomerSentiment`: positive | neutral | negative | mixed

### Where things live
- Taxonomy/label/color constants: `frontend/src/lib/taxonomy.ts` (single source of truth — import from here, don't redefine)
- Zod filter schema: `frontend/src/lib/schemas/interview-filters.ts`
- Backend aggregation logic: `backend/app/services/analytics_service.py`
- Seed script: `backend/scripts/seed_demo_data.py` (run with `python -m scripts.seed_demo_data` from `backend/`, not as a bare script, so the `app.*` imports resolve without the `sys.path` hack needing to kick in)
