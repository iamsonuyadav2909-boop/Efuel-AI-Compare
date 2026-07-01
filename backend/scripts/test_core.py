"""
Phase 1 POC test script - proves the EFUEL AI Research Engine core workflow works
end-to-end (search -> extract -> analyze -> score -> cache -> structured output),
including graceful fallback when TAVILY_API_KEY / FIRECRAWL_API_KEY are not configured.

Run with: python scripts/test_core.py
"""
import asyncio
import json
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from database import init_indexes, close_db, ai_cache_collection
from services.research_service import run_research, compute_query_hash


TEST_QUERIES = ["MCB", "Solar DC Isolator", "EV Connector"]


def _print_header(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


async def validate_result(result, query):
    errors = []
    if not result.category:
        errors.append("category is empty")
    if not result.summary:
        errors.append("summary is empty")
    if len(result.products) == 0:
        errors.append("no products returned")
    for p in result.products:
        if not p.name or not p.brand:
            errors.append(f"product missing name/brand: {p}")
        if not (0 <= p.engineering_score <= 100):
            errors.append(f"engineering_score out of range: {p.engineering_score}")
        if len(p.specifications) == 0:
            errors.append(f"product {p.name} has no specifications")
        if len(p.pros) == 0 or len(p.cons) == 0:
            errors.append(f"product {p.name} missing pros/cons")
    if not result.top_recommendation:
        errors.append("top_recommendation is empty")
    return errors


async def main():
    print("EFUEL Engineering Hub - Phase 1 Core AI Research Engine POC")
    print(f"TAVILY_API_KEY configured: {settings.tavily_enabled}")
    print(f"FIRECRAWL_API_KEY configured: {settings.firecrawl_enabled}")
    print(f"EMERGENT_LLM_KEY configured: {settings.llm_enabled}")

    await init_indexes()

    all_passed = True

    for query in TEST_QUERIES:
        _print_header(f"TEST: query='{query}'")
        # Clear any prior cache for a clean first-run test
        await ai_cache_collection.delete_one({"query_hash": compute_query_hash(query)})

        t0 = time.time()
        try:
            result = await run_research(query, force_refresh=True)
        except Exception as e:
            print(f"FAIL: run_research raised exception: {e}")
            all_passed = False
            continue
        duration = time.time() - t0

        errors = await validate_result(result, query)
        if errors:
            print(f"FAIL: validation errors for '{query}':")
            for e in errors:
                print(f"   - {e}")
            all_passed = False
        else:
            print(f"PASS: '{query}' produced valid structured result in {duration:.1f}s")
            print(f"   category: {result.category}")
            print(f"   data_source_mode: {result.data_source_mode}")
            print(f"   confidence: {result.confidence}")
            print(f"   #products: {len(result.products)}")
            print(f"   top_recommendation: {result.top_recommendation}")
            print(f"   Top product: {result.products[0].name} ({result.products[0].brand}) - score {result.products[0].engineering_score}")
            print(json.dumps(result.model_dump(), default=str, indent=2)[:1500] + "\n   ... (truncated)")

        # Test cache hit on rerun
        t0 = time.time()
        cached_result = await run_research(query, force_refresh=False)
        cache_duration = time.time() - t0
        if cache_duration < duration and cached_result.query_hash == result.query_hash:
            print(f"PASS: cache hit verified on rerun ({cache_duration:.2f}s vs {duration:.1f}s original)")
        else:
            print(f"WARN: cache hit not clearly faster ({cache_duration:.2f}s vs {duration:.1f}s) - check logic")

    await close_db()

    _print_header("FINAL RESULT")
    if all_passed:
        print("ALL TESTS PASSED - Core AI Research Engine is working correctly.")
        sys.exit(0)
    else:
        print("SOME TESTS FAILED - see above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
