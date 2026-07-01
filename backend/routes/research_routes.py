"""AI Research Engine routes - the core search workflow."""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
import uuid

from models_research import ResearchRequest, ResearchResult
from services.research_service import run_research
from auth import get_current_user
from database import search_history_collection, ai_cache_collection

router = APIRouter(prefix='/research', tags=['research'])


@router.post('', response_model=ResearchResult)
async def research(payload: ResearchRequest, current_user: dict = Depends(get_current_user)):
    from utils import check_rate_limit
    check_rate_limit(f"research:{current_user['id']}", max_requests=15, window_seconds=60)
    try:
        result = await run_research(payload.query, force_refresh=payload.force_refresh)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f'AI Research Engine error: {e}')

    await search_history_collection.insert_one({
        'id': str(uuid.uuid4()),
        'user_id': current_user['id'],
        'query': result.query,
        'category': result.category,
        'result_id': result.id,
        'top_product': result.products[0].name if result.products else '',
        'created_at': datetime.now(timezone.utc).isoformat(),
    })
    return result


@router.get('/history')
async def get_history(current_user: dict = Depends(get_current_user), limit: int = 20):
    cursor = search_history_collection.find({'user_id': current_user['id']}, {'_id': 0}) \
        .sort('created_at', -1).limit(limit)
    return await cursor.to_list(limit)


@router.get('', response_model=list)
async def list_cached(category: str = None, limit: int = 50, current_user: dict = Depends(get_current_user)):
    query = {}
    if category:
        query['category'] = {'$regex': category, '$options': 'i'}
    cursor = ai_cache_collection.find(query, {'_id': 0}).sort('created_at', -1).limit(limit)
    return await cursor.to_list(limit)


@router.get('/{result_id}', response_model=ResearchResult)
async def get_research_by_id(result_id: str, current_user: dict = Depends(get_current_user)):
    doc = await ai_cache_collection.find_one({'id': result_id}, {'_id': 0})
    if not doc:
        raise HTTPException(status_code=404, detail='Research result not found')
    return ResearchResult(**doc)
