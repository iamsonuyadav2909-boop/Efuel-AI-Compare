"""
Search provider orchestration - the entry point for EFUEL Engineering Hub's
Live Research Engine sourcing step.

Priority: Exa Search (primary, semantic) -> Tavily Search (fallback).
If neither provider is configured or both return zero results, the caller
(`services/research_service.py`) treats this as "no verified live manufacturer
data" and MUST NOT fall back to AI-only knowledge.

Future-ready / pluggable: to add a new provider (Google Custom Search, SerpAPI,
etc.), implement a `search_*(query, max_results)` function returning the same
`{enabled, results, answer}` contract and add it to the `PROVIDERS` list below.
No changes to research_service.py are required.
"""
import logging
from typing import Dict

from integrations.exa_client import search_exa_sources
from integrations.tavily_client import search_trusted_sources

logger = logging.getLogger(__name__)

# Ordered (provider_name, search_fn) pairs - first provider that returns usable
# live results wins. Order defines priority: Exa first, Tavily fallback.
PROVIDERS = [
    ('exa', search_exa_sources),
    ('tavily', search_trusted_sources),
]


async def run_search(query: str, max_results: int = 8) -> Dict:
    """Try each provider in priority order; return the first one with usable
    results. If none succeed, returns `{enabled: False, results: [], provider_used: None}`."""
    for provider_name, search_fn in PROVIDERS:
        try:
            data = await search_fn(query, max_results=max_results)
        except Exception as e:
            logger.error(f'Search provider "{provider_name}" raised an exception: {e}')
            continue

        if data.get('enabled') and data.get('results'):
            data['provider_used'] = provider_name
            logger.info(f'Search provider used: {provider_name} ({len(data["results"])} results) for query: {query}')
            return data
        elif data.get('enabled'):
            logger.info(f'Search provider "{provider_name}" is configured but returned 0 results; trying next provider')
        else:
            logger.info(f'Search provider "{provider_name}" is not configured; trying next provider')

    logger.warning(f'No search provider returned live results for query: {query}')
    return {'enabled': False, 'results': [], 'answer': '', 'provider_used': None}
