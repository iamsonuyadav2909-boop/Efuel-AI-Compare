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
- Build a **production-grade Admin platform** (Phase B):
  - Multi-user support + RBAC: **Super Admin, Admin, Engineer, Procurement, Viewer**
  - API Integration Manager with encrypted API keys stored in MongoDB (live-update without redeploy)
  - Search logs + AI logs, system settings
  - Full PDF/document management with **brand/product libraries**, **versioning**, **bulk operations**, and **enable/disable**
  - Rights to **clear Search History**
- **No UI redesign**: maintain existing EFUEL branding and reuse existing shadcn/Tailwind components.

**Current status (updated):**
- ✅ **Phase A is COMPLETE and tested** (backend + frontend).
- ✅ Exa Search API key is configured and verified live.
- ✅ No AI-knowledge fallback exists anywhere (strict no-data behavior enforced).
- ▶️ Phase B (Enterprise Admin + Multi-user + PDF management) is now starting.

---

## 2) Implementation Steps

### Phase 1 — Core AI Research Engine POC (Isolation) ✅ COMPLETE (legacy)
> Completed earlier; AI-knowledge fallback is now removed and no longer exists.

---

### Phase 2 — V1 App Build Around Proven Core ✅ COMPLETE (legacy baseline)
> Enterprise UI and core modules are complete and reused.

---

### Phase A (P0) — Strict Live-Search Enforcement + Exa Primary ✅ COMPLETE & VERIFIED
> Implemented and tested. This is the foundation for the enterprise platform.

#### A1) Foundational Infrastructure: Credential & Integration Layer ✅
**Goal:** live key updates without redeploy/restart; provider enable/disable; health + usage telemetry.

Delivered:
- ✅ `services/credential_service.py` (Fernet encryption; Mongo encrypted keys > env fallback)
- ✅ `CREDENTIAL_ENCRYPTION_KEY` configured
- ✅ Integration telemetry: last_success_at, last_error, usage_count

#### A2) Pluggable Search Providers ✅
Delivered:
- ✅ `integrations/domain_trust.py` shared trust scoring
- ✅ `integrations/exa_client.py` async REST client
- ✅ Tavily/Firecrawl/LLM clients refactored to use `credential_service`
- ✅ `services/search_orchestrator.py` (Exa → Tavily, future-ready extension point)

#### A3) Research Service Strict Pipeline Rewrite ✅
Delivered:
- ✅ `services/research_service.py` rewritten:
  - never calls LLM without verified live data
  - no-data returns strict exact message (and is not cached)
  - all returned products require source_urls (grounding safeguard)
- ✅ `models_research.py` updated: `no_data`, `message`, `search_provider_used`, `last_crawl_time`

#### A4) Frontend: Live-Verified UX ✅
Delivered:
- ✅ Live Verified badge semantics only (no “AI Expert Knowledge” mode)
- ✅ No-data state UI with exact message
- ✅ Sources tab shows verification details + citations
- ✅ Dashboard labels changed (“Not Configured” instead of “Fallback”)

#### A5) Testing & Verification ✅
- ✅ Backend verification: strict gating, exact message, caching rules, regressions (compare/bom/chat/etc.)
- ✅ Frontend verification: login, AI Search live/no-data states, Admin API keys display, no console errors

**Phase A Exit Criteria:** ✅ achieved

---

### Phase B (P0/P1) — Enterprise Admin + Multi-User + PDF Management (STARTING NOW)
> Must be implemented without redesigning the UI and without breaking existing features.

#### B0) Non-Negotiables (applies to all Phase B work)
- ✅ Do **not** reintroduce AI-only fallback anywhere.
- ✅ Do not break existing UI/flows; reuse existing shadcn components and EFUEL branding.
- ✅ Maintain SOLID/clean architecture: modular services and routers.
- ✅ Backwards compatibility: existing documents (auto-discovered external URLs) must still work.

#### B1) Multi-User Authentication + RBAC Expansion (P0)
**Goal:** transition from single-owner posture to enterprise multi-user with roles.

Backend tasks:
1. Update roles model:
   - `models_auth.py`: Role = Literal['super_admin','admin','engineer','procurement','viewer']
   - Define admin gate roles: `ADMIN_ROLES = ('super_admin','admin')`
2. Update permission checks:
   - `auth.py`: keep `require_roles` but update usage across routes to accept `super_admin` and `admin`
3. Auth routes:
   - Replace “single owner only” language/behavior
   - Add admin-managed user creation endpoints (Phase B2) instead of public registration
4. Data migration:
   - One-time migration: elevate current owner account to `role='super_admin'`

Frontend tasks:
5. `App.js` and `ProtectedRoute`:
   - `/admin` route roles must allow: `["admin", "super_admin"]`

**Testing:** verify login, admin access, and role gates.

#### B2) Complete Admin Panel Scope (P0)
Admin must manage:
- Users
- Roles
- Brands
- Categories
- Products
- Documents
- API Integrations
- Search Logs
- AI Logs
- System Settings

Backend tasks:
1. Modularize admin routes (recommended for maintainability):
   - `routes/admin_users_routes.py`
   - `routes/admin_catalog_routes.py` (brands/categories/products)
   - `routes/admin_documents_routes.py`
   - `routes/admin_integrations_routes.py`
   - `routes/admin_logs_routes.py` (search logs + AI logs)
   - `routes/admin_settings_routes.py`
2. Implement CRUD endpoints with pagination + filtering + audit logging.
3. Add rights to clear Search History:
   - `DELETE /api/admin/search-history` (clear all)
   - optional: `DELETE /api/admin/search-history/{id}`

Frontend tasks (no redesign, reuse components):
4. Expand `Admin.js` with new tabs:
   - Users, Roles, Brands, Categories, Products, Documents, API Integrations, Search Logs, AI Logs, System Settings
5. Add dialogs/forms with existing shadcn primitives.

#### B3) API Integration Manager (P0)
**Goal:** manage integrations dynamically from Admin without redeploy.

Backend tasks:
1. Persist integration state in Mongo (already supported by `credential_service`):
   - enable/disable
   - encrypted key
   - last success / last error
   - usage counters
2. Admin endpoints:
   - Update key (encrypted)
   - Toggle enable/disable
   - Test connection for each provider
   - View usage statistics
3. Provider selection (architecture now, UI later):
   - Ensure search provider selection remains pluggable via `search_orchestrator.py`
   - Keep AI provider abstraction via `LLM_PROVIDER`/`LLM_MODEL` (Admin UI will manage these in System Settings)

Frontend tasks:
4. Replace the current “API Keys” tab with “API Integrations”:
   - Enable/disable switch
   - Update key dialog
   - Test Connection button
   - Last success, last error, usage count, last sync

#### B4) PDF / Document Management System (P0/P1)
**Storage decision (confirmed):** Use **Emergent Object Storage** via `EMERGENT_LLM_KEY`.
- No new user credentials needed.
- Soft-delete pattern (storage has no delete API): DB is source of truth with `is_deleted`.

Requirements:
- Upload PDF
- Replace PDF
- Delete PDF (soft-delete)
- Edit metadata
- Preview PDF
- Download PDF
- Bulk upload
- Bulk delete
- Version control
- Enable/disable documents
- Brand-specific document libraries
- Product-specific document libraries

Backend tasks:
1. `services/storage_service.py` (NEW)
   - init_storage at startup (best-effort)
   - put_object / get_object
   - standardized path convention (app prefix + brand/product IDs + doc ID + version)
2. Document schema enhancements:
   - `documents` collection:
     - `storage_path`, `original_filename`, `content_type`, `size`
     - `brand_id` and/or `brand` mapping
     - `product_id` and/or `product_name` mapping
     - `is_active`, `is_deleted`
     - `current_version`, `versions[]` (each version has storage_path + created_at + checksum)
3. Admin routes:
   - upload
   - replace (new version)
   - update metadata
   - enable/disable
   - list by brand/product
   - preview/download endpoints that proxy storage via backend
   - bulk operations
4. Public/user document listing:
   - `GET /api/documents` must filter out deleted/inactive for non-admins

Frontend tasks:
5. Admin Documents tab:
   - Upload dialog (single + bulk)
   - Replace action
   - Metadata edit dialog
   - Preview dialog (iframe) using backend-proxied file URL
   - Download button
   - Enable/disable toggle
   - Version history UI + “set current version” (if required)
   - Bulk select + bulk delete
6. Non-admin Document Library (`Documents.js`):
   - Keep existing behavior for external URLs
   - For internal uploads, use backend-proxied file endpoint (query param token if needed for iframe)

#### B5) Logs: Search Logs & AI Logs (P0)
Backend tasks:
- Search Logs:
  - list
  - filter
  - export (optional)
  - clear (admin)
- AI Logs:
  - expose pipeline stage logs already in `api_logs`
  - add filtering by stage/provider/query/user

Frontend tasks:
- Add Admin tabs for Search Logs and AI Logs with filters and “clear” actions.

#### B6) System Settings (P1)
Backend tasks:
- Store system settings in Mongo (e.g., active providers, default model, UI defaults)
- Provide get/update endpoints.

Frontend tasks:
- Settings tab in Admin for:
  - LLM provider/model selection (Emergent LLM/OpenAI/Claude/Gemini)
  - default search provider priority (Exa first)
  - feature flags

---

## 3) Next Actions
### Phase A (Completed)
- ✅ Exa primary + Tavily fallback live
- ✅ strict no-data message enforced
- ✅ live-verified UI states confirmed

### Phase B (Immediate next)
1. Implement RBAC expansion (5 roles) + migrate owner to `super_admin`.
2. Expand Admin panel to full enterprise scope (tabs + backend endpoints).
3. Implement API Integration Manager operations (toggle, update keys, test connection).
4. Implement full PDF management using Emergent Object Storage with version control.
5. Add admin rights to clear Search History.
6. Run backend + frontend testing agents; fix regressions.

---

## 4) Success Criteria
### Phase A ✅
- Exa primary + Tavily fallback works
- No AI-only output is possible
- Exact no-data message returned when no verified live manufacturer data exists
- UI shows Live Verified status and citations; no “AI Expert Knowledge” exists

### Phase B (Target)
- Multi-user authentication with roles: Super Admin, Admin, Engineer, Procurement, Viewer
- Admin panel manages: Users, Roles, Brands, Categories, Products, Documents, API Integrations, Search Logs, AI Logs, System Settings
- API Integration Manager supports encrypted Mongo keys + enable/disable + test connection + usage stats
- Complete PDF/document management: upload/replace/delete/metadata/preview/download/bulk/versioning/enable-disable
- Admin can clear Search History
- No regressions: Search/Compare/BOM/Chat/Documents/Favorites/Library remain stable and smooth
