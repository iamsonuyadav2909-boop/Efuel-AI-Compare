"""
Tavily Search API integration - searches trusted engineering sources.
Gracefully disabled (returns empty) when TAVILY_API_KEY is not configured.
Prioritizes official manufacturer domains, datasheets, catalogues, authorized dealers,
with a focus on the Indian market (Indian distributors, INR pricing sources, BIS-certified products).
"""
import asyncio
import logging
from typing import List, Dict
from config import settings

logger = logging.getLogger(__name__)

# Known trusted manufacturer / engineering domains for EV Charger & Solar components.
# Indian entities listed first as they are prioritized for this deployment.
TRUSTED_DOMAINS = [
    # India-focused manufacturers, distributors & marketplaces
    'havells.com', 'polycab.com', 'rrkabel.com', 'legrand.co.in', 'schneider-electric.co.in',
    'lntebg.com', 'larsentoubro.com', 'crompton.co.in', 'cgglobal.com', 'hpl.in',
    'indoasian.com', 'standardelectricals.com', 'anchor-electricals.com', 'panasonic.com',
    'exicom.in', 'luminousindia.com', 'servokon.com', 'vguard.in', 'orientelectric.com',
    'finolex.com', 'kei-ind.com', 'apar.com', 'waaree.com', 'tatapower.com',
    'adanisolar.com', 'vikramsolar.com', 'goldiengroup.com', 'utlsolar.co.in',
    'amaron.com', 'exide.com', 'indiamart.com', 'tradeindia.com',
    # Global manufacturers with strong India presence
    'schneider-electric.com', 'se.com', 'abb.com', 'siemens.com', 'siemens-energy.com',
    'eaton.com', 'legrand.com', 'legrand.us', 'chint.com', 'chintglobal.com',
    'mennekes.de', 'phoenixcontact.com', 'te.com', 'huawei.com', 'sungrowpower.com',
    'growatt.com', 'solaredge.com', 'fimer.com', 'socomec.com', 'delta-electronics.com',
    'victronenergy.com', 'sma.de', 'ge.com', 'generalelectric.com', 'rittal.com',
    'weidmuller.com', 'omron.com', 'wago.com', 'finder.com', 'hager.com', 'rst.co.in',
    'staubli.com', 'amphenol-industrial.com', 'tesla.com', 'delta.com.tw', 'vestas.com',
    'canadiansolar.com', 'jinkosolar.com', 'trinasolar.com', 'longi.com', 'meanwell.com',
]

INDIA_TRUSTED_SUFFIXES = ('.co.in', '.in')


def _domain_trust_score(url: str) -> float:
    url_l = (url or '').lower()
    is_india_domain = any(url_l.split('/')[2].endswith(suf) if '://' in url_l and len(url_l.split('/')) > 2 else False for suf in INDIA_TRUSTED_SUFFIXES)
    for d in TRUSTED_DOMAINS:
        if d in url_l:
            return 0.98 if (d.endswith('.in') or '.co.in' in d) else 0.95
    if is_india_domain:
        return 0.85
    if any(k in url_l for k in ['datasheet', 'catalogue', 'catalog', 'spec', 'technical']):
        return 0.7
    if any(k in url_l for k in ['distributor', 'dealer', 'authorized']):
        return 0.6
    return 0.4


async def search_trusted_sources(query: str, max_results: int = 8) -> Dict:
    """
    Search trusted sources for a given component query, focused on the Indian market.
    Returns dict with `enabled`, `results` (list of {title, url, domain, trust_score, content}),
    and `answer` (Tavily's synthesized answer if available).
    """
    if not settings.tavily_enabled:
        logger.info('Tavily search skipped: TAVILY_API_KEY not configured (fallback mode)')
        return {'enabled': False, 'results': [], 'answer': ''}

    try:
        from tavily import AsyncTavilyClient
        client = AsyncTavilyClient(api_key=settings.TAVILY_API_KEY)

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
                'trust_score': _domain_trust_score(url),
                'content': r.get('content', ''),
            })

        # Sort by trust score (India-focused manufacturer sources first) then by relevance
        results.sort(key=lambda x: x['trust_score'], reverse=True)

        return {
            'enabled': True,
            'results': results,
            'answer': response.get('answer', ''),
        }
    except asyncio.TimeoutError:
        logger.error(f'Tavily search timed out for query: {query}')
        return {'enabled': True, 'results': [], 'answer': '', 'error': 'timeout'}
    except Exception as e:
        logger.error(f'Tavily search error for query "{query}": {e}')
        return {'enabled': True, 'results': [], 'answer': '', 'error': str(e)}
