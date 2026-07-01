"""
Core AI Research Engine - the heart of EFUEL Engineering Hub.

Workflow: User searches component -> Tavily searches trusted sources (if configured)
-> Firecrawl extracts specs from top manufacturer pages (if configured)
-> LLM analyzes (always, using live data when available, else expert engineering
   knowledge) -> generates structured engineering summary + Top 5 ranked products
   with Engineering Score -> cached in MongoDB -> returned to caller.

Designed to gracefully degrade: works fully even without TAVILY_API_KEY /
FIRECRAWL_API_KEY, and automatically upgrades to live-search mode the moment
those keys are configured - no code changes required.
"""
import hashlib
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from config import settings
from database import ai_cache_collection, api_logs_collection, products_collection, brands_collection
from models_research import ResearchResult, ProductResult, ScoreBreakdown, SourceRef
from integrations.tavily_client import search_trusted_sources
from integrations.firecrawl_client import extract_pages
from integrations.llm_client import generate_json

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 24 * 60 * 60  # 24 hours


def normalize_query(query: str) -> str:
    return ' '.join(query.strip().lower().split())


def compute_query_hash(query: str) -> str:
    return hashlib.sha256(normalize_query(query).encode('utf-8')).hexdigest()


async def _log_stage(stage: str, query: str, success: bool, duration_ms: float, meta: Optional[dict] = None):
    try:
        await api_logs_collection.insert_one({
            'stage': stage,
            'query': query,
            'success': success,
            'duration_ms': round(duration_ms, 2),
            'meta': meta or {},
            'created_at': datetime.now(timezone.utc).isoformat(),
        })
    except Exception as e:
        logger.error(f'Failed to log stage {stage}: {e}')


SYSTEM_MESSAGE = (
    "You are a senior electrical engineer and procurement specialist at EFUEL Engineering Hub in India, "
    "specializing in EV charging infrastructure and solar power components for the Indian market. You have "
    "deep, accurate knowledge of real brands available in India (Havells, Polycab, RR Kabel, Legrand, "
    "Schneider Electric, L&T, Crompton, CG Power, HPL, Indo Asian, Anchor by Panasonic, Exicom, Luminous, "
    "Waaree, Vikram Solar, Adani Solar, Tata Power Solar, UTL Solar, as well as global brands sold in India "
    "like ABB, Siemens, Eaton, Chint, Mennekes, Phoenix Contact, Huawei, Sungrow, SolarEdge, Delta "
    "Electronics, Victron Energy, SMA, Fimer, Socomec, Omron, WAGO, Finder, Hager, Amphenol, etc.) and their "
    "real product lines, technical specifications, certifications (BIS/ISI, IEC, CE, UL, RoHS), and "
    "industrial applications in EV charging and solar/electrical protection systems. Prioritize products "
    "genuinely available for purchase in India, and always give pricing in Indian Rupees (INR, use the ₹ "
    "symbol). You always respond with strict, valid, parseable JSON only - no markdown fences, no "
    "commentary, no explanations outside the JSON object."
)


def _build_prompt(query: str, tavily_data: dict, firecrawl_data: dict) -> tuple:
    """Returns (prompt_text, data_source_mode)"""
    live_context_parts = []
    if tavily_data.get('answer'):
        live_context_parts.append(f"Search summary: {tavily_data['answer']}")
    for r in tavily_data.get('results', [])[:6]:
        if r.get('content'):
            live_context_parts.append(f"[Source: {r.get('url')}]\n{r.get('content')[:800]}")
    for p in firecrawl_data.get('pages', []):
        if p.get('markdown'):
            live_context_parts.append(f"[Extracted from: {p.get('url')}]\n{p.get('markdown')[:2000]}")

    has_live_data = len(live_context_parts) > 0
    data_source_mode = 'live_search' if has_live_data else 'llm_knowledge'

    if has_live_data:
        context_block = (
            "Here is real-time data gathered from official manufacturer sources and trusted "
            "engineering websites:\n--- SOURCE DATA START ---\n" + "\n\n".join(live_context_parts)[:9000] +
            "\n--- SOURCE DATA END ---\nUse this real data as your primary reference, filling minor "
            "gaps with your accurate expert engineering knowledge of these real products."
        )
    else:
        context_block = (
            "No live web search data is currently available for this request (live search/crawl "
            "integrations are not yet configured by the administrator). Use your accurate expert "
            "engineering knowledge of REAL, currently-manufactured products from major brands. "
            "Do not invent fictional brands or models - only reference real, verifiable products."
        )

    prompt = f"""Research the following electrical/EV-charging/solar component category: "{query}"

{context_block}

IMPORTANT MARKET FOCUS: This research is exclusively for the INDIAN market. Only recommend products that
are genuinely available for purchase in India (via authorized Indian distributors, Indian manufacturer
subsidiaries, or major Indian industrial suppliers like IndiaMART/TradeIndia-listed authorized dealers).
Prefer Indian brands (Havells, Polycab, RR Kabel, L&T, Crompton, CG Power, HPL, Indo Asian, Anchor, Exicom,
Luminous, Waaree, Vikram Solar, Adani Solar, Tata Power Solar, UTL Solar) where a genuinely competitive
Indian product exists, and international brands with an established India presence (ABB India, Siemens
India, Schneider Electric India, Legrand India, Chint, etc.) otherwise. ALL pricing MUST be given in
Indian Rupees (₹ / INR) as the primary currency.

Your task:
1. Identify the correct normalized component category name.
2. Identify the TOP 5 best REAL products (brand + specific model/series) AVAILABLE IN INDIA, currently used in 
   EV charging, solar, and industrial electrical projects for this category.
3. For EACH of the 5 products provide ALL of these fields:
   - name (specific model/series name)
   - brand (manufacturer name)
   - specifications: at least 5 realistic technical specs as {{"name":..,"value":..,"unit":..}}
   - score_breakdown: technical_quality, reliability, brand_reputation, industrial_usage, warranty,
     certification, performance, availability, compatibility -- each a number 0-10
   - engineering_score: overall weighted score 0-100 (based on score_breakdown)
   - pros: list of 3-5 strings
   - cons: list of 2-4 strings
   - engineering_notes: 1-3 sentence expert engineering note
   - compatibility: list of compatible systems/standards/voltage classes
   - industrial_applications: list of 2-4 real-world use cases
   - alternatives: list of 2-3 alternative product/brand names (available in India)
   - certifications: list e.g. ["BIS", "IS 8828", "IEC 60947-2", "CE"]
   - source_urls: list of URLs actually referenced from source data above (empty list if none/fallback mode)
   - ai_recommendation: 1-2 sentence recommendation
   - estimated_price_range: price range in Indian Rupees, formatted like "₹1,200 - ₹1,800" (INR only, no other currency)
4. Rank the 5 products by engineering_score, highest first (rank 1 = best).
5. Provide "summary": 2-4 sentence overview of this component category & key buying considerations
   for EV/solar engineering projects in India.
6. Provide "top_recommendation": name of rank-1 product + why, in one sentence.
7. Provide "best_value": name of the most cost-effective good-quality product among the 5.
8. Provide "confidence": float 0-1 (use ~0.9 if live source data was provided above, ~0.65 if 
   relying on expert knowledge only).

Return ONLY a valid raw JSON object with EXACTLY this structure (no markdown, no extra text):
{{
  "category": "string",
  "summary": "string",
  "products": [
    {{
      "rank": 1,
      "name": "string",
      "brand": "string",
      "engineering_score": 92.5,
      "score_breakdown": {{"technical_quality":9,"reliability":9,"brand_reputation":9,"industrial_usage":9,"warranty":8,"certification":9,"performance":9,"availability":8,"compatibility":9}},
      "specifications": [{{"name":"Rated Current","value":"63","unit":"A"}}],
      "pros": ["string"],
      "cons": ["string"],
      "engineering_notes": "string",
      "compatibility": ["string"],
      "industrial_applications": ["string"],
      "alternatives": ["string"],
      "certifications": ["string"],
      "source_urls": ["string"],
      "ai_recommendation": "string",
      "estimated_price_range": "₹1,200 - ₹1,800"
    }}
  ],
  "top_recommendation": "string",
  "best_value": "string",
  "confidence": 0.9
}}"""
    return prompt, data_source_mode


async def _persist_products_and_docs(result: ResearchResult):
    """Persist researched products/brands/documents into their own collections so the
    Component Library, Admin Panel and Document Library reflect REAL research data
    (never mocked). Idempotent upserts keyed by (name, brand) / url."""
    from database import documents_collection

    for p in result.products:
        try:
            now_iso = datetime.now(timezone.utc).isoformat()
            await products_collection.update_one(
                {'name': p.name, 'brand': p.brand},
                {
                    '$set': {
                        'name': p.name,
                        'brand': p.brand,
                        'category': result.category,
                        'engineering_score': p.engineering_score,
                        'score_breakdown': p.score_breakdown.model_dump(),
                        'specifications': [s.model_dump() for s in p.specifications],
                        'pros': p.pros,
                        'cons': p.cons,
                        'engineering_notes': p.engineering_notes,
                        'compatibility': p.compatibility,
                        'industrial_applications': p.industrial_applications,
                        'alternatives': p.alternatives,
                        'certifications': p.certifications,
                        'source_urls': p.source_urls,
                        'ai_recommendation': p.ai_recommendation,
                        'estimated_price_range': p.estimated_price_range,
                        'updated_at': now_iso,
                    },
                    '$setOnInsert': {'id': str(uuid.uuid4()), 'created_at': now_iso},
                },
                upsert=True,
            )
            await brands_collection.update_one(
                {'name': p.brand},
                {'$setOnInsert': {'name': p.brand, 'created_at': now_iso}},
                upsert=True,
            )
        except Exception as e:
            logger.warning(f'Could not persist product {p.name}: {e}')

    for src in result.sources:
        url_l = (src.url or '').lower()
        if any(k in url_l for k in ['.pdf', 'datasheet', 'catalogue', 'catalog', 'manual']):
            doc_type = (
                'datasheet' if 'datasheet' in url_l or url_l.endswith('.pdf')
                else 'catalogue' if 'catalog' in url_l
                else 'manual' if 'manual' in url_l
                else 'reference'
            )
            try:
                now_iso = datetime.now(timezone.utc).isoformat()
                await documents_collection.update_one(
                    {'url': src.url},
                    {
                        '$setOnInsert': {
                            'id': str(uuid.uuid4()),
                            'title': src.title or result.category,
                            'url': src.url,
                            'doc_type': doc_type,
                            'category': result.category,
                            'brand': '',
                            'product_name': '',
                            'source': 'auto',
                            'created_at': now_iso,
                        }
                    },
                    upsert=True,
                )
            except Exception as e:
                logger.warning(f'Could not persist document {src.url}: {e}')


async def run_research(query: str, force_refresh: bool = False) -> ResearchResult:
    """Main entrypoint for the AI Research Engine core workflow."""
    query = query.strip()
    query_hash = compute_query_hash(query)

    # 1. Cache lookup
    if not force_refresh:
        cached = await ai_cache_collection.find_one({'query_hash': query_hash}, {'_id': 0})
        if cached:
            age = (datetime.now(timezone.utc) - datetime.fromisoformat(cached['created_at'])).total_seconds()
            cached_mode = cached.get('data_source_mode')
            live_now_available = settings.tavily_enabled or settings.firecrawl_enabled
            is_stale_fallback = cached_mode == 'llm_knowledge' and live_now_available
            if age < CACHE_TTL_SECONDS and not is_stale_fallback:
                logger.info(f'Cache HIT for query: {query}')
                return ResearchResult(**cached)
            if is_stale_fallback:
                logger.info(f'Cache INVALIDATED for query: {query} (was llm_knowledge, live search now available)')
            else:
                logger.info(f'Cache STALE for query: {query} (age={age:.0f}s)')

    # 2. Tavily search (trusted sources)
    t0 = time.time()
    tavily_data = await search_trusted_sources(query)
    await _log_stage('tavily_search', query, tavily_data.get('enabled', False) and len(tavily_data.get('results', [])) > 0,
                      (time.time() - t0) * 1000, {'enabled': tavily_data.get('enabled'), 'result_count': len(tavily_data.get('results', []))})

    # 3. Firecrawl extraction (top trusted URLs)
    t0 = time.time()
    top_urls = [r['url'] for r in tavily_data.get('results', [])[:3] if r.get('url')]
    firecrawl_data = await extract_pages(top_urls) if top_urls else {'enabled': settings.firecrawl_enabled, 'pages': []}
    await _log_stage('firecrawl_extract', query, len(firecrawl_data.get('pages', [])) > 0,
                      (time.time() - t0) * 1000, {'enabled': firecrawl_data.get('enabled'), 'pages_scraped': len(firecrawl_data.get('pages', []))})

    # 4. LLM Analysis
    t0 = time.time()
    prompt, data_source_mode = _build_prompt(query, tavily_data, firecrawl_data)
    parsed = await generate_json(SYSTEM_MESSAGE, prompt)
    llm_success = parsed is not None
    await _log_stage('llm_analyze', query, llm_success, (time.time() - t0) * 1000, {'data_source_mode': data_source_mode})

    if not parsed:
        raise RuntimeError('LLM analysis failed to produce a valid structured result. Please try again.')

    # 5. Build structured ResearchResult
    products = []
    for p in parsed.get('products', [])[:5]:
        try:
            breakdown_raw = p.get('score_breakdown', {}) or {}
            breakdown = ScoreBreakdown(**{k: float(v) for k, v in breakdown_raw.items() if k in ScoreBreakdown.model_fields})
            eng_score = p.get('engineering_score')
            if eng_score is None:
                vals = [getattr(breakdown, f) for f in ScoreBreakdown.model_fields]
                eng_score = (sum(vals) / len(vals)) * 10 if vals else 0
            products.append(ProductResult(
                rank=int(p.get('rank', len(products) + 1)),
                name=p.get('name', 'Unknown'),
                brand=p.get('brand', 'Unknown'),
                engineering_score=round(float(eng_score), 1),
                score_breakdown=breakdown,
                specifications=[{'name': s.get('name', ''), 'value': str(s.get('value', '')), 'unit': s.get('unit', '')} for s in p.get('specifications', [])],
                pros=p.get('pros', []) or [],
                cons=p.get('cons', []) or [],
                engineering_notes=p.get('engineering_notes', ''),
                compatibility=p.get('compatibility', []) or [],
                industrial_applications=p.get('industrial_applications', []) or [],
                alternatives=p.get('alternatives', []) or [],
                certifications=p.get('certifications', []) or [],
                source_urls=p.get('source_urls', []) or [],
                ai_recommendation=p.get('ai_recommendation', ''),
                estimated_price_range=p.get('estimated_price_range', ''),
            ))
        except Exception as e:
            logger.error(f'Error parsing product entry: {e} | raw={p}')
            continue

    products.sort(key=lambda x: x.rank)

    sources = [SourceRef(title=r.get('title', ''), url=r.get('url', ''), domain=r.get('domain', ''), trust_score=r.get('trust_score', 0)) for r in tavily_data.get('results', [])]

    result = ResearchResult(
        query=query,
        category=parsed.get('category', query),
        summary=parsed.get('summary', ''),
        products=products,
        top_recommendation=parsed.get('top_recommendation', ''),
        best_value=parsed.get('best_value', ''),
        confidence=float(parsed.get('confidence', 0.6)),
        data_source_mode=data_source_mode,
        sources=sources,
        query_hash=query_hash,
    )

    # 6. Cache in MongoDB (upsert)
    doc = result.model_dump()
    doc['created_at'] = result.created_at.isoformat()
    doc['updated_at'] = datetime.now(timezone.utc).isoformat()
    await ai_cache_collection.update_one(
        {'query_hash': query_hash},
        {'$set': doc},
        upsert=True,
    )

    await _persist_products_and_docs(result)

    return result
