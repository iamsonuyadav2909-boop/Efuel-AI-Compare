# EFUEL Engineering Hub — Updated Plan (Live-Verified Enterprise Edition)

## 1) Objectives
- Deliver a **STRICT Live Research Engine** with a non-negotiable workflow:
  **Search (Exa → Tavily) → Crawl (Firecrawl) → Extract → AI Analysis → Recommendation**.
- **Zero hallucinations / zero AI-only fallback**: the system must **never** generate specs or recommendations without verified live sources.
- If verified live manufacturer data cannot be found, return **only** the exact message:
  > "No verified live manufacturer data was found for this product. Please check your search query or configure Exa/Tavily and Firecrawl API keys."
- Introduce a **future-ready modular architecture**:
  - Pluggable search providers (Exa, Tavily now; Google CSE, SerpAPI future)
  - Pluggable AI providers (Emergent LLM now; OpenAI/Claude/Gemini future)
- Build a **production-grade Admin platform** (after Phase A is verified):
  - Multi-user support + RBAC: **Super Admin, Admin, Engineer, Procurement, Viewer**
  - API Integration Manager with encrypted API keys stored in MongoDB (live-update without redeploy)
  - Search logs, AI logs, system settings
  - Full PDF/document management with brand/product libraries and version control
- **No UI redesign**: maintain existing EFUEL branding and reuse existing shadcn/Tailwind components.

**Current status (important correction):**
- The app currently operates with **AI expert-knowledge fallback mode**. This is now **explicitly forbidden** and will be removed in Phase A.

---

## 2) Implementation Steps

### Phase 1 — Core AI Research Engine POC (Isolation) ✅ COMPLETE (legacy)
> Completed earlier, but parts of this phase (AI-knowledge fallback) are now **obsolete and must be removed**.

**Delivered previously:** ✅
- Tavily + Firecrawl + LLM integrations
- Research pipeline + caching
- UI/UX and app modules

**Now deprecated:** ❌
- Any behavior that allows LLM to answer from internal knowledge when no sources exist.

---

### Phase 2 — V1 App Build Around Proven Core ✅ COMPLETE (legacy baseline)
> The enterprise UI and application modules are complete and will be **reused**.

**Delivered previously:** ✅
- Dashboard, AI Search, Compare, BOM, Documents, Assistant, Favorites/History, Settings
- Admin baseline screens and endpoints (limited)

**Now requires Phase A refactor:**
- Replace “AI Expert Knowledge” mode across backend + UI with **Live Verified only** semantics.

---

### Phase A (NEW P0) — Strict Live-Search Enforcement + Exa Primary (IN PROGRESS)
> This is the immediate focus. Must be completed and tested before Phase B.

#### A1) Foundational Infrastructure: Credential & Integration Layer (P0)
**Goal:** allow live key updates without redeploy/restart; enforce provider enable/disable; capture health + usage.

Backend tasks:
1. **`config.py`**
   - Add `EXA_API_KEY` setting (env fallback).
   - Add `CREDENTIAL_ENCRYPTION_KEY` (required for Mongo-encrypted key storage).
2. **`backend/.env`**
   - Append placeholders:
     - `EXA_API_KEY=""`
     - `CREDENTIAL_ENCRYPTION_KEY="..."` (generated for dev; production rotated securely)
3. **`services/credential_service.py`** (NEW)
   - Implement encrypted API-key storage in MongoDB using Fernet:
     - Priority order: **Mongo encrypted keys > environment variables**
   - Provide:
     - `get_api_key(provider)`
     - `set_api_key(provider, key)`
     - `set_provider_enabled(provider, enabled)`
     - `record_success(provider, meta)` / `record_error(provider, error)`
     - `get_integration_status()` (last success, last error, enabled, usage stats, last sync)
   - Schema design in `system_settings` (or new `api_integrations`) collection:
     - provider, enabled, encrypted_key, last_success_at, last_error, usage counters, last_sync_at

#### A2) Pluggable Search Providers (P0)
**Goal:** Exa first, Tavily second, future providers plug-in without changing research logic.

Backend tasks:
4. **Shared trust scoring module**
   - Create `integrations/domain_trust.py` extracting trust logic from `tavily_client.py`.
5. **`integrations/exa_client.py`** (NEW)
   - Implement Exa Search API client using direct REST via `httpx` (async-friendly):
     - If `EXA_API_KEY` missing/unavailable: return `{enabled: False, results: []}` and let orchestrator fallback.
     - Return results in the same contract as Tavily: `{enabled, results, answer}`.
     - Capture: url, title, domain, content/highlights where possible, trust_score.
6. **Refactor `integrations/tavily_client.py`**
   - Fetch key via `credential_service.get_api_key('tavily')`.
   - Use `domain_trust.py` for scoring.
7. **Refactor `integrations/firecrawl_client.py`**
   - Fetch key via `credential_service.get_api_key('firecrawl')`.
8. **Refactor `integrations/llm_client.py`**
   - Fetch key via `credential_service.get_api_key('emergent_llm')`.
   - (Still used only after live data exists.)
9. **`services/search_orchestrator.py`** (NEW)
   - Provider priority list: `[exa, tavily]`.
   - “First-success-wins” logic:
     - choose provider that returns usable results
     - track `provider_used`
   - Prepare extension points for Google CSE / SerpAPI.

#### A3) Research Service Strict Pipeline Rewrite (P0)
**Goal:** eliminate hallucinations; enforce strict error messaging and avoid caching false results.

Backend tasks:
10. **Rewrite `services/research_service.py`**
   - Remove **all** `llm_knowledge` / AI-only paths.
   - New strict flow:
     1) Search via `search_orchestrator` (Exa→Tavily)
     2) Crawl top URLs via Firecrawl
     3) If **no verified live content** found (no results + no extracted pages):
        - Return `no_data=True` and **only** the exact message string (no LLM call, no speculation).
     4) If live content exists:
        - Build prompt that **forces** AI to only use provided citations.
        - Allow fewer than 5 products if evidence is limited.
     5) If LLM fails to produce valid result or yields empty/uncited products:
        - Return strict no-data message.
   - Caching rules:
     - Cache only successful live-verified results.
     - Do **not** cache “no verified live manufacturer data” failures.

11. **Update `models_research.py`**
   Add fields needed by UI and auditing:
   - `no_data: bool = False`
   - `message: str = ''` (used only when `no_data=True`)
   - `search_provider_used: str = ''` (exa|tavily)
   - `last_crawl_time: Optional[str]`
   - Update `data_source_mode` to always be `live_search` on success; remove/stop using `llm_knowledge` in logic.

12. **Update system status endpoints to include Exa + integration manager state**
   - `server.py` `/api/health`: include `exa_configured`/enabled and aggregated status.
   - `routes/admin_routes.py`:
     - extend current `/api-keys/status` to include Exa and integration manager-backed status.
   - `routes/misc_routes.py` dashboard summary: change labels (not “fallback”), reflect “configured/enabled/healthy”.

#### A4) Frontend: Live-Verified UX (No Redesign) (P0)
**Goal:** remove AI-knowledge messaging; show live verification fields and the strict no-data message.

Frontend tasks (reuse existing components):
13. **`DataSourceBadge.js`**
   - Replace “AI Expert Knowledge” language.
   - Use “Live Verified Data” (shield/check icon). (If needed, show “Degraded/Not Configured” separately, but never “AI mode”.)
14. **`AISearch.js`**
   - If `result.no_data === true`, render a dedicated EmptyState/Alert block and display the **exact** message.
   - Do not render ranked results panel in no-data state.
15. **`ProductResultCard.js` (Sources tab)**
   - Replace the old fallback text.
   - Display live verification details:
     - Source URLs
     - Page title/domain where available
     - Last crawl time
     - Manufacturer/brand attribution if known
16. **`Dashboard.js` + `Settings.js`**
   - Rename statuses from “Fallback” to “Not Configured” / “Disabled” / “Degraded”, aligned to integration manager.

#### A5) Testing & Verification (P0)
Backend tests (must pass):
- Exa key missing ⇒ Exa disabled ⇒ Tavily runs normally.
- Exa + Tavily both unavailable ⇒ `/api/research` returns **only** strict no-data message.
- Firecrawl unavailable or returns zero pages ⇒ treated as “no verified live manufacturer data”.
- No AI-only responses returned anywhere.
- Compare/BOM/Chat unaffected by refactor (regression check).

Frontend tests (must pass):
- AI Search no-data UX renders exact message.
- Live Verified badge appears only for success.
- Sources tab shows citations; no “AI Expert Knowledge” text remains.

**Phase A Exit Criteria (Definition of Done):**
- It is impossible for the system to return product specs/recommendations without live sources.
- The exact no-data message is returned under all failure/no-source conditions.
- Exa integration is implemented and ready; if key is absent it gracefully falls back to Tavily.

---

### Phase B (P0/P1) — Enterprise Admin + Multi-User + Document Management (NOT STARTED)
> Begins only after Phase A is verified working.

#### B1) Multi-User Authentication + RBAC Expansion (P0)
- Remove “single-owner only” restriction.
- Roles:
  - Super Admin
  - Admin
  - Engineer
  - Procurement
  - Viewer
- Update:
  - `models_auth.py` roles enum
  - Auth routes and seeding strategy (no wiping users)
  - Route permissions (`require_roles`) across modules

#### B2) Admin Panel: Complete Enterprise Scope (P0)
Admin should manage:
- Users
- Roles
- Brands
- Categories
- Products
- Documents
- API Integrations (Integration Manager)
- Search Logs
- AI Logs
- System Settings

Backend:
- Expand `admin_routes.py` into modular routers (recommended):
  - `admin_users_routes.py`, `admin_integrations_routes.py`, `admin_documents_routes.py`, etc.
- Add CRUD endpoints with pagination, filtering, and audit logging.

Frontend:
- Reuse existing `Admin.js` tabs and components; extend without redesign.

#### B3) API Integration Manager UI + Operations (P0)
For each integration (Exa, Tavily, Firecrawl, Emergent LLM, future APIs):
- Enable/Disable toggle
- Update key (stored encrypted in Mongo)
- Test Connection button
- Last Successful Connection
- Last Error
- Usage Statistics
- Last Sync Time
- Provider switching controls (search + AI) without code changes

#### B4) PDF / Document Management System (P0/P1)
Features:
- Upload PDF, replace, delete
- Edit metadata
- Preview + download
- Bulk upload / bulk delete
- Version control
- Enable/disable documents
- Brand-specific document library
- Product-specific document library

Backend:
- Decide storage strategy (local/S3-compatible) and implement signed download URLs if needed.
- Add document version schema.

Frontend:
- Extend existing Documents UI; add Admin workflows.

---

## 3) Next Actions
**Immediate (Phase A, now):**
1. Implement credential_service + EXA integration client + search_orchestrator.
2. Rewrite research_service to strict live-only behavior and exact error message.
3. Update UI components to remove AI-knowledge references and support no-data state.
4. Run backend + frontend testing agents; fix regressions.

**After Phase A verified:**
5. Start Phase B: multi-user RBAC overhaul.
6. Build Admin Integration Manager UI backed by encrypted keys in Mongo.
7. Implement full PDF management with versioning + brand/product libraries.

---

## 4) Success Criteria
- **Phase A:**
  - Exa primary + Tavily fallback works (Exa gracefully disabled if key missing).
  - No AI-only output is possible.
  - Exact no-data message returned when no verified live manufacturer data exists.
  - UI shows Live Verified status and citations; no “AI Expert Knowledge” strings remain.

- **Phase B:**
  - Multi-user authentication with 5 roles.
  - Admin Panel fully manages enterprise entities and logs.
  - Integration Manager supports encrypted Mongo-stored keys, enable/disable, test connection, usage stats.
  - Complete PDF/document management with version control and per-brand/per-product libraries.
