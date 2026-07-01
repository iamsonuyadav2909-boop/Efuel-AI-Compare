"""
Firecrawl API integration - extracts structured technical content from manufacturer pages.
Gracefully disabled (returns empty) when FIRECRAWL_API_KEY is not resolvable.
"""
import asyncio
import logging
from typing import List, Dict

from services import credential_service

logger = logging.getLogger(__name__)


async def _scrape_one(client, url: str) -> Dict:
    try:
        result = await asyncio.wait_for(
            client.scrape(url=url, formats=['markdown']),
            timeout=30,
        )
        markdown = getattr(result, 'markdown', None) or (result.get('markdown') if isinstance(result, dict) else '') or ''
        return {'url': url, 'markdown': markdown[:6000], 'success': True}
    except asyncio.TimeoutError:
        logger.warning(f'Firecrawl scrape timed out for {url}')
        return {'url': url, 'markdown': '', 'success': False, 'error': 'timeout'}
    except Exception as e:
        logger.warning(f'Firecrawl scrape error for {url}: {e}')
        return {'url': url, 'markdown': '', 'success': False, 'error': str(e)}


async def extract_pages(urls: List[str], max_pages: int = 3) -> Dict:
    """
    Scrape a list of URLs (already prioritized by trust) and return cleaned markdown content.
    """
    api_key = await credential_service.get_api_key('firecrawl')
    if not api_key:
        logger.info('Firecrawl extraction skipped: FIRECRAWL_API_KEY not configured')
        return {'enabled': False, 'pages': []}

    try:
        from firecrawl import AsyncFirecrawl
        client = AsyncFirecrawl(api_key=api_key)

        targets = urls[:max_pages]
        tasks = [_scrape_one(client, u) for u in targets]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        pages = [r for r in results if r.get('success')]
        if pages:
            await credential_service.record_success('firecrawl')
        return {'enabled': True, 'pages': pages}
    except Exception as e:
        logger.error(f'Firecrawl client init/extraction error: {e}')
        await credential_service.record_error('firecrawl', str(e))
        return {'enabled': True, 'pages': [], 'error': str(e)}
