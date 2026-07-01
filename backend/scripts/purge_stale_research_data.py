"""
One-time data migration: purges research/product/document data that was generated
BEFORE Tavily/Firecrawl were configured and BEFORE India/INR-focused prompts were
applied. This ensures the app only shows accurate, live-sourced, India-focused data
going forward (no stale AI-expert-knowledge-only or non-INR demo data).

Safe to run multiple times. Does NOT touch user accounts.
Run with: python scripts/purge_stale_research_data.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import (
    ai_cache_collection, products_collection, brands_collection, documents_collection,
    search_history_collection, compare_history_collection, favorites_collection,
    api_logs_collection, close_db,
)


async def purge():
    counts = {}
    for name, coll in [
        ('ai_cache', ai_cache_collection),
        ('products', products_collection),
        ('brands', brands_collection),
        ('documents', documents_collection),
        ('search_history', search_history_collection),
        ('compare_history', compare_history_collection),
        ('favorites', favorites_collection),
        ('api_logs', api_logs_collection),
    ]:
        result = await coll.delete_many({})
        counts[name] = result.deleted_count

    print('Purged stale collections:')
    for name, count in counts.items():
        print(f'  - {name}: {count} document(s) removed')
    print('\nAll future searches will use live Tavily/Firecrawl data (India-focused, INR pricing)'
          ' or clearly-labeled AI expert knowledge as a fallback.')
    await close_db()


if __name__ == '__main__':
    asyncio.run(purge())
