"""AI Compare Engine routes."""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
import uuid

from models_app import CompareRequest
from services.compare_service import compare_products
from auth import get_current_user
from database import compare_history_collection
from utils import check_rate_limit

router = APIRouter(prefix='/compare', tags=['compare'])


@router.post('')
async def compare(payload: CompareRequest, current_user: dict = Depends(get_current_user)):
    if len(payload.products) < 2 or len(payload.products) > 4:
        raise HTTPException(status_code=400, detail='Please select between 2 and 4 products to compare.')
    check_rate_limit(f"compare:{current_user['id']}", max_requests=10, window_seconds=60)
    try:
        result = await compare_products(payload.products, payload.query_category)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f'AI Compare Engine error: {e}')

    doc = {
        'id': str(uuid.uuid4()),
        'user_id': current_user['id'],
        'product_names': [p.get('name', '') for p in payload.products],
        'category': payload.query_category,
        'result': result,
        'created_at': datetime.now(timezone.utc).isoformat(),
    }
    await compare_history_collection.insert_one(dict(doc))
    return {'id': doc['id'], 'product_names': doc['product_names'], **result}


@router.get('/history')
async def get_compare_history(current_user: dict = Depends(get_current_user), limit: int = 20):
    cursor = compare_history_collection.find({'user_id': current_user['id']}, {'_id': 0}) \
        .sort('created_at', -1).limit(limit)
    return await cursor.to_list(limit)
