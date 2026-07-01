# EFUEL Engineering Hub

An internal AI-powered engineering & procurement platform for EV Charger and Solar
components. Engineers and procurement teams search any component (MCB, MCCB, SPD,
Contactor, Relay, Energy Meter, Solar Inverter, DC Isolator, MC4, Solar Cable, EV
Connector, SMPS, Power Supply, Cooling Fan, Enclosure, etc.) and the AI Research Engine
automatically searches trusted sources, extracts technical specifications, analyzes
quality, and returns a ranked Top-5 recommendation with an Engineering Score.

## Tech Stack

| Layer      | Technology |
|------------|------------|
| Frontend   | React 19, React Router, Tailwind CSS, shadcn/ui (Radix), Framer Motion |
| Backend    | FastAPI (async), Motor (async MongoDB driver) |
| Database   | MongoDB |
| Auth       | JWT (PyJWT + bcrypt), Role-Based Access Control (Admin / Engineer / Viewer) |
| AI         | Emergent Universal LLM Key via `emergentintegrations` (OpenAI GPT-4o) |
| Search     | Tavily Search API (trusted-source web search) |
| Crawl      | Firecrawl API (manufacturer page extraction) |

> **Note on stack adaptation:** The original spec requested Next.js + Supabase +
> PostgreSQL. Per explicit user confirmation, the app was built on the platform's
> native, fully-supported stack (React + FastAPI + MongoDB) to guarantee stability and
> compatibility, while preserving 100% of the functional requirements.

## Core AI Research Workflow

```
User searches component (e.g. "MCB")
        |
        v
Tavily Search API -- searches trusted manufacturer sites/datasheets/catalogues
        |  (gracefully skipped if TAVILY_API_KEY not configured)
        v
Firecrawl API -- extracts specs/tables/markdown from top trusted URLs
        |  (gracefully skipped if FIRECRAWL_API_KEY not configured)
        v
Emergent LLM (GPT-4o) -- analyzes data (or expert knowledge if no live data)
        |  generates: category summary, Top-5 ranked products, Engineering Score,
        |  pros/cons, compatibility, alternatives, certifications, source citations
        v
MongoDB `ai_cache` -- result cached (24h TTL) + products/brands/documents persisted
        v
Structured JSON returned to the frontend and rendered
```

This pipeline was proven in isolation via `backend/scripts/test_core.py` before the
full application was built around it (see Phase 1 POC in `/app/plan.md`).

**Graceful degradation:** If `TAVILY_API_KEY` / `FIRECRAWL_API_KEY` are not configured,
the engine automatically falls back to AI expert-knowledge mode (clearly labeled as
"AI Expert Knowledge" vs "Live Search Data" in the UI) -- no code changes are needed to
activate live search once real keys are added.

## Folder Structure

```
/app
|-- backend/
|   |-- server.py                # FastAPI app entrypoint, mounts /api router
|   |-- config.py                # Centralized settings (env vars)
|   |-- database.py              # Motor client, collections, indexes
|   |-- auth.py                  # JWT + bcrypt + RBAC dependencies
|   |-- utils.py                 # serialize_doc, rate limiter
|   |-- models_auth.py           # User/auth Pydantic schemas
|   |-- models_app.py            # Favorites/Documents/BOM/Chat/Compare schemas
|   |-- models_research.py       # AI Research Engine schemas (ResearchResult, etc.)
|   |-- integrations/
|   |   |-- tavily_client.py     # Trusted-source web search
|   |   |-- firecrawl_client.py  # Manufacturer page extraction
|   |   `-- llm_client.py        # Emergent LLM Key wrapper (structured JSON + chat)
|   |-- services/
|   |   |-- research_service.py  # Core AI Research Engine (search->extract->analyze->cache)
|   |   |-- compare_service.py   # AI Compare Engine
|   |   |-- bom_service.py       # AI BOM Builder
|   |   `-- chat_service.py      # AI Assistant (grounded chat)
|   |-- routes/                  # auth, research, compare, chat, bom, misc, admin
|   `-- scripts/
|       |-- test_core.py         # Phase 1 POC test (search/extract/analyze/cache)
|       `-- seed_users.py        # Seeds demo Admin/Engineer/Viewer accounts
|
|-- frontend/
|   `-- src/
|       |-- App.js               # Routes (code-split via React.lazy)
|       |-- context/             # AuthContext, ThemeContext
|       |-- lib/                 # api.js (axios), compareBasket.js, utils.js
|       |-- components/
|       |   |-- layout/          # AppShell, SidebarNav, Header, ProtectedRoute
|       |   |-- shared/          # ScoreGauge, ProductResultCard, SpecTable, etc.
|       |   `-- ui/              # shadcn/ui primitives
|       `-- pages/               # Dashboard, AISearch, Compare, ComponentLibrary,
|                                   ComponentCategory, ProductDetail, Documents,
|                                   BOMBuilder, AIAssistant, Favorites,
|                                   RecentSearches, Settings, Admin, Login, Register
|
`-- plan.md                      # Living implementation plan & phase status
```

## API Documentation (all routes prefixed with `/api`)

### Auth
- `POST /auth/register` -- `{name, email, password, role}` -> `{access_token, user}`
- `POST /auth/login` -- `{email, password}` -> `{access_token, user}`
- `GET /auth/me` -- current user (Bearer token)

### AI Research Engine
- `POST /research` -- `{query, force_refresh}` -> `ResearchResult` (category, summary,
  top 5 ranked products with engineering scores, sources, data_source_mode)
- `GET /research` -- list cached research (filter by `category`)
- `GET /research/history` -- current user's search history
- `GET /research/{id}` -- fetch a cached result by id

### Compare Engine
- `POST /compare` -- `{products: [...2-4 product objects], query_category}` -> AI
  comparison (winner_overall, best_value, best_industrial, spec_comparison, etc.)
- `GET /compare/history`

### AI Assistant
- `POST /chat` -- `{message, session_id}` -> `{session_id, reply}` (grounded in cached research)
- `GET /chat/sessions`, `GET /chat/sessions/{id}`

### BOM Builder
- `POST /bom/generate` -- `{project_name, requirement}` -> generated BOM
- `GET /bom/projects`, `GET /bom/projects/{id}`, `DELETE /bom/projects/{id}`
- `GET /bom/projects/{id}/export/{csv|xlsx|pdf}` -- file download

### Favorites / Documents / Library / Dashboard
- `POST /favorites`, `GET /favorites`, `DELETE /favorites/{id}`
- `GET /documents`, `POST /documents` (engineer/admin)
- `GET /categories` -- fixed 7-category taxonomy + component lists
- `GET /products`, `GET /products/{id}`, `GET /brands`
- `GET /dashboard/summary` -- aggregated dashboard widgets data

### Admin (admin role only)
- `GET /admin/users`, `PUT /admin/users/{id}/role`, `PUT /admin/users/{id}/status`
- `GET /admin/brands`, `DELETE /admin/brands/{name}`
- `GET /admin/categories`, `POST /admin/categories`, `DELETE /admin/categories/{name}`
- `GET /admin/products`, `DELETE /admin/products/{id}`
- `GET /admin/documents`, `DELETE /admin/documents/{id}`
- `GET /admin/logs` -- AI pipeline stage logs (tavily_search/firecrawl_extract/llm_analyze)
- `GET /admin/api-keys/status` -- Tavily/Firecrawl/Emergent LLM configuration status

Interactive OpenAPI docs available at `{BACKEND_URL}/docs` (FastAPI auto-generated).

## Environment Variables

**Backend** (`/app/backend/.env`):
```
MONGO_URL, DB_NAME, CORS_ORIGINS
EMERGENT_LLM_KEY, LLM_PROVIDER, LLM_MODEL
TAVILY_API_KEY        # placeholder -- add to enable live trusted-source search
FIRECRAWL_API_KEY     # placeholder -- add to enable live manufacturer extraction
JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES
```

**Frontend** (`/app/frontend/.env`): `REACT_APP_BACKEND_URL` (pre-configured, do not modify)

## Enabling Live Search (Tavily + Firecrawl)

1. Obtain a Tavily API key at https://tavily.com and a Firecrawl API key at
   https://firecrawl.dev
2. Add them to `/app/backend/.env`:
   ```
   TAVILY_API_KEY="tvly-..."
   FIRECRAWL_API_KEY="fc-..."
   ```
3. Restart the backend: `sudo supervisorctl restart backend`
4. No code changes required -- the AI Research Engine automatically switches from
   "AI Expert Knowledge" to "Live Search Data" mode.

## Demo Credentials

| Role     | Email               | Password     |
|----------|---------------------|--------------|
| Admin    | admin@efuel.com     | Admin@123    |
| Engineer | engineer@efuel.com  | Engineer@123 |
| Viewer   | viewer@efuel.com    | Viewer@123   |

Re-seed anytime with: `cd /app/backend && python scripts/seed_users.py`

**Remove or rotate these credentials before any external/production deployment.**

## Development

Services are managed by `supervisord` -- hot reload is enabled for both frontend and
backend. Restart only after installing new dependencies or editing `.env`:

```bash
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
```

Run the Phase 1 core POC test anytime to verify the AI Research Engine pipeline:
```bash
cd /app/backend && python scripts/test_core.py
```

## Deployment Guide

1. Ensure all required env vars are set in `backend/.env` (Tavily/Firecrawl optional
   but recommended for production-grade live sourcing).
2. Rotate `JWT_SECRET` to a strong random value and remove/rotate demo credentials.
3. Set `CORS_ORIGINS` to your actual frontend domain(s) instead of `*`.
4. Use the platform's Deploy action -- it builds the frontend and runs the backend under
   supervisor automatically. No manual `uvicorn`/`npm start` needed.
5. MongoDB indexes are created automatically on backend startup (`init_indexes()`).
6. Monitor `/api/health` for integration status (`tavily_configured`,
   `firecrawl_configured`, `llm_configured`).
