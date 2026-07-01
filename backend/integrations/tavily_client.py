"""
Tavily Search API integration - FALLBACK search provider (used when Exa is not
configured or returns zero results - see services/search_orchestrator.py).
Gracefully disabled (returns empty) when TAVILY_API_KEY is not resolvable.
Prioritizes official manufacturer domains, datasheets, catalogues, authorized dealers,
with a focus on the Indian market (Indian distributors, INR pricing sources, BIS-certified products).
"""
import asyncio
import logging
from typing import List, Dict

from services import credential_service
from integrations.domain_trust import domain_trust_score

logger = logging.getLogger(__name__)


async def search_trusted_sources(query: str, max_results: int = 8) -> Dict:
    """
    Search trusted sources for a given component query, focused on the Indian market.
    Returns dict with `enabled`, `results` (list of {title, url, domain, trust_score, content}),
    and `answer` (Tavily's synthesized answer if available).
    """
    api_key = await credential_service.get_api_key('tavily')
    if not api_key:
        logger.info('Tavily search skipped: TAVILY_API_KEY not configured')
        return {'enabled': False, 'results': [], 'answer': ''}

    try:
        from tavily import AsyncTavilyClient
        client = AsyncTavilyClient(api_key=api_key)

        search_query = (
            f"{query} technical datasheet specifications India price BIS certified manufacturer distributor"
        )

        response = await asyncio.wait_for(
            client.search(
                query=search_query,
                search_depth='advanced',
                max_results=max_results,
                include_answer=True,
                topic='general',
                country='india',
            ),
            timeout=25,
        )

        results = []
        for r in response.get('results', []):
            url = r.get('url', '')
            domain = url.split('/')[2] if '://' in url and len(url.split('/')) > 2 else url
            results.append({
                'title': r.get('title', ''),
                'url': url,
                'domain': domain,
                'trust_score': domain_trust_score(url),
                'content': r.get('content', ''),
            })

        # Sort by trust score (India-focused manufacturer sources first) then by relevance
        results.sort(key=lambda x: x['trust_score'], reverse=True)

        await credential_service.record_success('tavily')
        return {
            'enabled': True,
            'results': results,
            'answer': response.get('answer', ''),
        }
    except asyncio.TimeoutError:
        logger.error(f'Tavily search timed out for query: {query}')
        await credential_service.record_error('tavily', 'Request timed out')
        return {'enabled': True, 'results': [], 'answer': '', 'error': 'timeout'}
    except Exception as e:
        logger.error(f'Tavily search error for query "{query}": {e}')
        await credential_service.record_error('tavily', str(e))
        return {'enabled': True, 'results': [], 'answer': '', 'error': str(e)}
