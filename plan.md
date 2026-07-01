# EFUEL Engineering Hub — Plan

## 1) Objectives
- Deliver a **working AI Research Engine core** (search → extract → analyze → score → cache → structured output) with **graceful fallback** when Tavily/Firecrawl keys are missing.
- Build a premium, engineer-friendly internal platform around the proven core: Dashboard, AI Search, Compare, Library, Documents, BOM Builder, AI Assistant, Favorites/History, Settings, Dark Mode.
- Add Admin + production hardening: user mgmt, API key mgmt UI, logs, rate limits, caching/indexes, security.

---

## 2) Implementation Steps

### Phase 1 — Core AI Research Engine POC (Isolation) ✅ (do not proceed until green)
**User stories (POC):**
1. As an engineer, I can run a script with a component query and receive a structured JSON engineering summary.
2. As an engineer, I can see an engineering score + top ranked products even when external API keys are missing.
3. As an engineer, I can provide Tavily/Firecrawl keys later without changing code (only env/UI config).
4. As an engineer, I can re-run the same query and get a cached result instead of recomputation.
5. As an admin, I can inspect the pipeline step status (search/extract/analyze) and errors from logs.

**Steps:**
1. **Best-practice websearch (targeted):** resilient pipeline patterns (retry/backoff), schema-first structured outputs, caching strategy (Mongo indexes), trusted-domain allowlist patterns.
2. Add backend modules (no UI yet):
   - `integrations/tavily_client.py` (enabled only if `TAVILY_API_KEY` present)
   - `integrations/firecrawl_client.py` (enabled only if `FIRECRAWL_API_KEY` present)
   - `integrations/llm_client.py` using **EMERGENT_LLM_KEY** (OpenAI-compatible), schema-first JSON output
3. Define core schemas (Pydantic):
   - `ResearchResult` (query, normalized category, sources, extracted_specs, summary, pros/cons, compat, alternatives, ranked_products[], engineering_score, confidence, notes)
4. Implement pipeline service:
   - `research_service.run(query)`:
     - cache lookup (hash query + params)
     - Tavily search (if enabled) → trusted URL selection (allowlist + heuristics)
     - Firecrawl extract (if enabled) → normalize specs
     - LLM analyze (always) → produce `ResearchResult`
     - scoring (deterministic function + LLM fields) → top 5 ranking
     - persist to `ai_cache` collection with timestamps + source URLs
     - return structured result
   - Implement retry/backoff + timeouts for external calls; clean error types.
5. Create `scripts/test_core.py`:
   - Runs 3 queries (e.g., MCB/MCCB/SPD), prints JSON, validates schema, verifies cache hit on rerun.
6. Add Mongo collections + indexes:
   - `ai_cache` (query_hash unique, created_at, updated_at)
   - `api_logs` (pipeline events)
7. **POC acceptance run:** execute script with missing keys (fallback mode) and verify still passes; if keys added later, pipeline auto-upgrades.

**Deliverables:** working `test_core.py`, stable backend research module, Mongo caching, env placeholders.

---

### Phase 2 — V1 App Build Around Proven Core (MVP, premium UX; auth deferred)
**User stories (V1 app):**
1. As an engineer, I can use AI Search to research a component and view a clean spec/summary layout.
2. As an engineer, I can open a product detail view with sources, docs links, and extracted specs.
3. As an engineer, I can compare up to 4 researched products side-by-side and get an AI winner.
4. As an engineer, I can chat with an AI assistant grounded in cached results for follow-up questions.
5. As an engineer, I can browse component categories and quickly find commonly used parts.

**Steps:**
1. Frontend design foundation (React + Tailwind + shadcn + Framer Motion):
   - App shell: Sidebar (nav), Header (global search, breadcrumbs, profile), responsive layout
   - Theme system: light/dark, EFUEL branding tokens (blue/black/white), typography scale
2. Backend API (wrap Phase 1 service):
   - `POST /api/research` (query) → returns cached or fresh `ResearchResult`
   - `GET /api/research/:id` or `GET /api/research?query=`
   - `POST /api/compare` (product ids) → returns comparison object + winner
   - `POST /api/chat` (messages + optional context ids) → assistant response
3. UI Pages (MVP complete flows):
   - Dashboard (key widgets: Quick Search, Recent Searches, Top Recommendations, System/API status)
   - AI Search (search → loading skeleton → results view: score card, ranked list, specs table, sources)
   - Compare (select up to 4 from recent/cached → comparison table + recommendation)
   - Component Library (category browse + basic detail page pulling cached research)
   - AI Assistant (chat UI with context chips)
   - Settings (show Tavily/Firecrawl key status as “Not configured” + instructions; no key entry yet)
4. Data persistence for V1:
   - `recent_searches`, `favorites` (local first, then backend endpoints if time)
5. Call **design_agent** after Phase 1, before finalizing Phase 2 UI: finalize EFUEL design system + reusable components.
6. End-to-end test pass (testing agent): search → view → compare → chat; verify loading/error/empty states.

**Deliverables:** fully usable internal V1 without auth; premium dashboard + AI search/compare/chat; stable API.

---

### Phase 3 — Add Features + Auth + Enterprise Completeness
**User stories (features + auth):**
1. As a user, I can log in and only see internal EFUEL data relevant to my role.
2. As an engineer, I can save favorites and access them across devices.
3. As a procurement user, I can build a BOM from a requirement and export it.
4. As an engineer, I can manage documents (view, search, preview PDFs) tied to components.
5. As a user, I can see my search/compare history and resume work instantly.

**Steps:**
1. JWT auth + RBAC (Admin/Engineer/Viewer):
   - `/api/auth/register|login|me` + route guards
   - seed users + write `/app/memory/test_credentials.md`
2. Documents Library:
   - store document metadata + links; PDF preview UI; search/filter
3. Favorites + History:
   - backend collections: `favorites`, `search_history`, `compare_history`
4. BOM Builder:
   - `POST /api/bom/generate` (requirement) → structured BOM + notes + alternates
   - export: CSV first (MVP), then PDF
5. Settings upgrade:
   - placeholders for Tavily/Firecrawl key entry UI (masked) and status; persist to `system_settings` (optional) or keep env-only with UI guidance.
6. Testing agent: authenticated flows + BOM + docs + favorites.

---

### Phase 4 — Admin Panel + Production Hardening
**User stories (admin/hardening):**
1. As an admin, I can manage users and roles safely.
2. As an admin, I can manage brands/categories/products/docs without breaking research results.
3. As an admin, I can view API/system logs and investigate failures.
4. As an admin, I can configure API key status and monitor integration health.
5. As a user, I get fast, reliable results due to caching, indexes, and background processing.

**Steps:**
1. Admin UI: Users/Roles, Brands, Categories, Products, Documents, System Settings, Logs.
2. Backend hardening:
   - rate limiting, strict validation, standardized error envelope
   - background jobs for long research (optional queue-lite)
   - caching improvements + Mongo indexes; TTL where appropriate
3. Observability:
   - `api_logs` viewer, pipeline timing metrics
4. Production readiness:
   - README + architecture docs + API docs + deployment notes.
5. Testing agent: regression suite across all major flows.

---

## 3) Next Actions
1. Run Phase 1 websearch + finalize schemas and scoring rubric.
2. Implement Phase 1 backend integration layer + `scripts/test_core.py` + Mongo cache.
3. Execute POC tests (fallback mode) until consistently green.
4. Call design_agent to lock EFUEL design system.
5. Build Phase 2 V1 app in one cohesive pass (app shell + pages + API wiring) then run E2E tests.

---

## 4) Success Criteria
- **Phase 1:** `scripts/test_core.py` produces valid schema JSON, deterministic score, and cache hit on rerun; Tavily/Firecrawl integrations are implemented and auto-enable when keys appear.
- **Phase 2:** UI delivers a premium dashboard + AI Search/Compare/Assistant flows with correct loading/empty/error states; no broken navigation; responsive + dark mode.
- **Phase 3:** Auth + RBAC works; favorites/history persist; BOM + documents usable end-to-end.
- **Phase 4:** Admin CRUD + logs + rate limiting + caching/indexes in place; documented deployment and stable regression results.
