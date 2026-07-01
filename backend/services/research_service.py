"""
Core AI Research Engine - the heart of EFUEL Engineering Hub.

STRICT LIVE-SEARCH-ONLY WORKFLOW (non-negotiable):

    Search (Exa -> Tavily fallback) -> Crawl (Firecrawl) -> Extract -> AI Analysis -> Recommendation

The AI is NEVER permitted to answer from its own internal knowledge. If no verified
live manufacturer data can be found by the search/crawl pipeline, the engine returns
the exact message defined in `NO_DATA_MESSAGE` below and performs NO LLM call at all.
When live data IS found, the LLM is instructed to ground every product strictly in
the provided source data - it may return fewer than 5 products, but must never invent
brands, models or specs that are not evidenced in the sources.
"""
import hashlib
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from database import ai_cache_collection, api_logs_collection, products_collection, brands_collection
from models_research import ResearchResult, ProductResult, ScoreBreakdown, SourceRef
from services.search_orchestrator import run_search
from integrations.firecrawl_client import extract_pages
from integrations.llm_client import generate_json

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 24 * 60 * 60  # 24 hours

# Exact, non-negotiable message returned whenever no verified live manufacturer data
# can be found. Never alter this wording - it is a strict user requirement.
NO_DATA_MESSAGE = (
    "No verified live manufacturer data was found for this product. Please check your "
    "search query or configure Exa/Tavily and Firecrawl API keys."
)


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
    "specializing in EV charging infrastructure and solar power components for the Indian market. You are "
    "given REAL, live-crawled source data gathered moments ago from manufacturer/distributor websites and "
    "search engines. Your ONLY job is to extract, organize, structure and score the products that are "
    "ACTUALLY PRESENT in that source data - you must NEVER supplement it with your own background "
    "knowledge, invent products, or guess specifications that are not evidenced in the provided text. "
    "You always respond with strict, valid, parseable JSON only - no markdown fences, no commentary, no "
    "explanations outside the JSON object."
)


def _build_prompt(query: str, live_context_parts: list) -> str:
    """Build the strict, source-grounded prompt. Only ever called when live_context_parts
    is non-empty (i.e. verified live data exists)."""
    context_block = (
        "Here is REAL, live data gathered moments ago from search engines and manufacturer/distributor "
        "websites for this exact query:\n--- SOURCE DATA START ---\n" +
        "\n\n".join(live_context_parts)[:11000] +
        "\n--- SOURCE DATA END ---"
    )

    prompt = f"""Analyze the following live source data to research this electrical/EV-charging/solar
component category: "{query}"

{context_block}

CRITICAL GROUNDING RULES (must be followed exactly):
1. You may ONLY report products, brands, models and specifications that are explicitly mentioned or
   strongly evidenced by the SOURCE DATA above. Do NOT invent, assume, or add products/specs from your
   own general knowledge - this is a strict compliance requirement, not a stylistic preference.
2. If the source data only clearly evidences 1, 2 or 3 distinct real products, return ONLY that many
   products - never pad the list with fabricated products to reach 5. A shorter, accurate list is
   required over a longer, invented one.
3. Every product's "source_urls" field MUST contain only URLs that were actually part of the source data
   above and that specifically relate to that product.
4. For any specification, price, or certification not explicitly present in the source data, you may
   state a value ONLY if it is a widely-published, verifiable spec of that exact real product from
   your training knowledge AND it does not contradict the source data. If truly unknown, use
   "Not specified in sources" rather than guessing.
5. If, after reviewing the source data, you cannot identify ANY real, specific product (brand + model),
   return an empty "products" array - do not force an answer.

IMPORTANT MARKET FOCUS: This research is exclusively for the INDIAN market. Prefer products genuinely
available for purchase in India. ALL pricing MUST be given in Indian Rupees (₹ / INR) as the primary
currency, and ONLY if pricing is evidenced in or reasonably inferable from the source data - otherwise
state "Not specified in sources".

Your task:
1. Identify the correct normalized component category name.
2. Identify up to 5 REAL products (brand + specific model/series) that are evidenced in the source data,
   ranked by engineering merit. Return fewer than 5 if the data does not support more.
3. For EACH product provide ALL of these fields:
   - name (specific model/series name)
   - brand (manufacturer name)
   - specifications: technical specs evidenced in the source data, as {{"name":..,"value":..,"unit":..}}
   - score_breakdown: technical_quality, reliability, brand_reputation, industrial_usage, warranty,
     certification, performance, availability, compatibility -- each a number 0-10
   - engineering_score: overall weighted score 0-100 (based on score_breakdown)
   - pros: list of 2-5 strings
   - cons: list of 1-4 strings
   - engineering_notes: 1-3 sentence expert engineering note grounded in the source data
   - compatibility: list of compatible systems/standards/voltage classes
   - industrial_applications: list of 2-4 real-world use cases
   - alternatives: list of 0-3 alternative product/brand names (ONLY if evidenced in the source data)
   - certifications: list e.g. ["BIS", "IS 8828", "IEC 60947-2", "CE"] (only if evidenced)
   - source_urls: list of URLs from the source data above that specifically relate to this product
     (MUST NOT be empty for any product you include - if you cannot cite a source, do not include the product)
   - ai_recommendation: 1-2 sentence recommendation grounded in the source data
   - estimated_price_range: price range in Indian Rupees like "₹1,200 - ₹1,800", or "Not specified in sources"
4. Rank the products by engineering_score, highest first (rank 1 = best).
5. Provide "summary": 2-4 sentence overview of this component category grounded in the source data.
6. Provide "top_recommendation": name of rank-1 product + why, in one sentence (empty string if no products).
7. Provide "best_value": name of the most cost-effective good-quality product (empty string if no products).
8. Provide "confidence": float 0-1 reflecting how well the source data supports these findings.

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
    return prompt


def _collect_live_context(search_data: dict, firecrawl_data: dict) -> list:
    """Gathers all verified live text snippets from the search + crawl stages."""
    live_context_parts = []
    if search_data.get('answer'):
        live_context_parts.append(f"Search summary: {search_data['answer']}")
    for r in search_data.get('results', [])[:6]:
        if r.get('content'):
            live_context_parts.append(f"[Source: {r.get('url')}]\n{r.get('content')[:800]}")
    for p in firecrawl_data.get('pages', []):
        if p.get('markdown'):
            live_context_parts.append(f"[Extracted from: {p.get('url')}]\n{p.get('markdown')[:2000]}")
    return live_context_parts


def _no_data_result(query: str, query_hash: str, search_provider_used: str = '') -> ResearchResult:
    return ResearchResult(
        query=query,
        category=query,
        summary='',
        products=[],
        top_recommendation='',
        best_value='',
        confidence=0.0,
        data_source_mode='no_data',
        no_data=True,
        message=NO_DATA_MESSAGE,
        search_provider_used=search_provider_used,
        last_crawl_time=None,
        sources=[],
        query_hash=query_hash,
    )


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
                            'is_active': True,
                            'is_deleted': False,
                            'created_at': now_iso,
                        }
                    },
                    upsert=True,
                )
            except Exception as e:
                logger.warning(f'Could not persist document {src.url}: {e}')


async def run_research(query: str, force_refresh: bool = False) -> ResearchResult:
    """Main entrypoint for the AI Research Engine's strict live-search-only workflow."""
    query = query.strip()
    query_hash = compute_query_hash(query)

    # 1. Cache lookup - ONLY ever return previously successful, live-verified results.
    if not force_refresh:
        cached = await ai_cache_collection.find_one(
            {'query_hash': query_hash, 'data_source_mode': 'live_search', 'no_data': {'$ne': True}},
            {'_id': 0},
        )
        if cached:
            age = (datetime.now(timezone.utc) - datetime.fromisoformat(cached['created_at'])).total_seconds()
            if age < CACHE_TTL_SECONDS:
                logger.info(f'Cache HIT for query: {query}')
                return ResearchResult(**cached)
            logger.info(f'Cache STALE for query: {query} (age={age:.0f}s)')

    # 2. Search (Exa primary -> Tavily fallback)
    t0 = time.time()
    search_data = await run_search(query)
    provider_used = search_data.get('provider_used') or ''
    await _log_stage('search', query, bool(search_data.get('results')), (time.time() - t0) * 1000, {
        'provider_used': provider_used,
        'result_count': len(search_data.get('results', [])),
    })

    # 3. Firecrawl extraction (top trusted URLs from search results)
    t0 = time.time()
    top_urls = [r['url'] for r in search_data.get('results', [])[:3] if r.get('url')]
    firecrawl_data = await extract_pages(top_urls) if top_urls else {'enabled': False, 'pages': []}
    await _log_stage('firecrawl_extract', query, len(firecrawl_data.get('pages', [])) > 0,
                      (time.time() - t0) * 1000, {'enabled': firecrawl_data.get('enabled'), 'pages_scraped': len(firecrawl_data.get('pages', []))})

    live_context_parts = _collect_live_context(search_data, firecrawl_data)

    # 4. STRICT GATE: no verified live data anywhere -> return the exact no-data message.
    # NEVER call the LLM in this branch and NEVER cache this outcome (so a retry after
    # configuring API keys, or a transient network blip, works immediately).
    if not live_context_parts:
        logger.warning(f'No verified live manufacturer data found for query: "{query}" (provider={provider_used or "none"})')
        await _log_stage('no_data_gate', query, False, 0, {'provider_used': provider_used})
        return _no_data_result(query, query_hash, provider_used)

    # 5. LLM Analysis - strictly grounded in the live source data collected above.
    t0 = time.time()
    prompt = _build_prompt(query, live_context_parts)
    parsed = await generate_json(SYSTEM_MESSAGE, prompt)
    llm_success = parsed is not None and bool(parsed.get('products'))
    await _log_stage('llm_analyze', query, llm_success, (time.time() - t0) * 1000, {'provider_used': provider_used})

    if not parsed or not parsed.get('products'):
        logger.warning(f'LLM could not extract any grounded products from live data for query: "{query}"')
        return _no_data_result(query, query_hash, provider_used)

    # 6. Build structured ResearchResult
    products = []
    for p in parsed.get('products', [])[:5]:
        try:
            # Grounding safeguard: skip any product the model failed to cite a source for.
            if not p.get('source_urls'):
                logger.warning(f'Dropping ungrounded product "{p.get("name")}" (no source_urls cited)')
                continue
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

    # If every candidate product was dropped by the grounding safeguard, treat as no-data.
    if not products:
        logger.warning(f'All candidate products were ungrounded/dropped for query: "{query}"')
        return _no_data_result(query, query_hash, provider_used)

    products.sort(key=lambda x: x.rank)

    sources = [SourceRef(title=r.get('title', ''), url=r.get('url', ''), domain=r.get('domain', ''), trust_score=r.get('trust_score', 0)) for r in search_data.get('results', [])]
    now_iso = datetime.now(timezone.utc).isoformat()

    result = ResearchResult(
        query=query,
        category=parsed.get('category', query),
        summary=parsed.get('summary', ''),
        products=products,
        top_recommendation=parsed.get('top_recommendation', ''),
        best_value=parsed.get('best_value', ''),
        confidence=float(parsed.get('confidence', 0.6)),
        data_source_mode='live_search',
        no_data=False,
        message='',
        search_provider_used=provider_used,
        last_crawl_time=now_iso,
        sources=sources,
        query_hash=query_hash,
    )

    # 7. Cache in MongoDB (upsert) - only successful, live-verified results are ever cached.
    doc = result.model_dump()
    doc['created_at'] = result.created_at.isoformat()
    doc['updated_at'] = now_iso
    await ai_cache_collection.update_one(
        {'query_hash': query_hash},
        {'$set': doc},
        upsert=True,
    )

    await _persist_products_and_docs(result)

    return result
