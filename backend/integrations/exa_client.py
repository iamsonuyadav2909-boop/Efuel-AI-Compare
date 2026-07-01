"""
Exa Search API integration (https://exa.ai) - PRIMARY semantic search provider for
manufacturer datasheets, technical specifications and pricing pages.

Gracefully disabled (returns `enabled: False`) whenever no EXA_API_KEY is resolvable
(neither Admin-configured in MongoDB nor set via env). The `search_orchestrator`
module automatically falls back to Tavily in that case - no code changes required
when a key is added later via the Admin Panel or `.env`.

Uses a direct async REST call (httpx) to Exa's `/search` endpoint with `contents`
(text + highlights) so no separate crawl step is needed for the search results
themselves (Firecrawl is still used afterwards for deeper extraction of the top
URLs - see services/research_service.py).
"""
import logging
from typing import Dict

import httpx

from services import credential_service
from integrations.domain_trust import domain_trust_score

logger = logging.getLogger(__name__)

EXA_SEARCH_URL = 'https://api.exa.ai/search'


async def search_exa_sources(query: str, max_results: int = 8) -> Dict:
    """
    Search trusted sources for a given component query via Exa's neural/semantic
    search, focused on the Indian market. Returns the same contract as
    `tavily_client.search_trusted_sources`: `{enabled, results, answer}` so both
    providers are interchangeable inside `search_orchestrator.py`.
    """
    api_key = await credential_service.get_api_key('exa')
    if not api_key:
        logger.info('Exa search skipped: EXA_API_KEY not configured (will fall back to Tavily)')
        return {'enabled': False, 'results': [], 'answer': ''}

    search_query = (
        f"{query} technical datasheet specifications India price BIS certified manufacturer distributor"
    )
    body = {
        'query': search_query,
        'type': 'auto',
        'numResults': max_results,
        'contents': {
            'text': {'maxCharacters': 2000},
            'highlights': {'query': query, 'numSentences': 3, 'highlightsPerUrl': 2},
        },
    }
    headers = {'x-api-key': api_key, 'Content-Type': 'application/json'}

    try:
        async with httpx.AsyncClient(timeout=25) as client:
            resp = await client.post(EXA_SEARCH_URL, json=body, headers=headers)

        if resp.status_code == 401:
            await credential_service.record_error('exa', 'Unauthorized (401): invalid or revoked EXA_API_KEY')
            logger.error('Exa search error: invalid API key (401)')
            return {'enabled': True, 'results': [], 'answer': '', 'error': 'unauthorized'}
        if resp.status_code == 402:
            await credential_service.record_error('exa', 'Payment required (402): quota exhausted')
            logger.error('Exa search error: quota exhausted (402)')
            return {'enabled': True, 'results': [], 'answer': '', 'error': 'quota_exhausted'}
        resp.raise_for_status()
        data = resp.json()

        results = []
        for r in data.get('results', []):
            url = r.get('url', '')
            domain = url.split('/')[2] if '://' in url and len(url.split('/')) > 2 else url
            content_parts = []
            if r.get('text'):
                content_parts.append(r['text'])
            highlights = r.get('highlights') or []
            if highlights:
                content_parts.append(' '.join(highlights))
            results.append({
                'title': r.get('title', '') or '',
                'url': url,
                'domain': domain,
                'trust_score': domain_trust_score(url),
                'content': '\n'.join(content_parts)[:2000],
            })

        results.sort(key=lambda x: x['trust_score'], reverse=True)
        await credential_service.record_success('exa')
        return {'enabled': True, 'results': results, 'answer': ''}
    except httpx.TimeoutException:
        logger.error(f'Exa search timed out for query: {query}')
        await credential_service.record_error('exa', 'Request timed out')
        return {'enabled': True, 'results': [], 'answer': '', 'error': 'timeout'}
    except Exception as e:
        logger.error(f'Exa search error for query "{query}": {e}')
        await credential_service.record_error('exa', str(e))
        return {'enabled': True, 'results': [], 'answer': '', 'error': str(e)}
