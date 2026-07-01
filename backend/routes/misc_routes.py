"""Favorites, Documents, Categories, Products, Brands, Dashboard routes."""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
import uuid

from models_app import FavoriteCreate, DocumentCreate
from auth import get_current_user, require_roles
from database import (
    favorites_collection, documents_collection, search_history_collection,
    compare_history_collection, ai_cache_collection, products_collection, brands_collection,
)
from config import settings

router = APIRouter(tags=['misc'])

# ---- Favorites ----


@router.post('/favorites')
async def add_favorite(payload: FavoriteCreate, current_user: dict = Depends(get_current_user)):
    existing = await favorites_collection.find_one(
        {'user_id': current_user['id'], 'product_name': payload.product_name, 'brand': payload.brand}
    )
    if existing:
        existing.pop('_id', None)
        return existing
    doc = payload.model_dump()
    doc['id'] = str(uuid.uuid4())
    doc['user_id'] = current_user['id']
    doc['created_at'] = datetime.now(timezone.utc).isoformat()
    await favorites_collection.insert_one(dict(doc))
    return doc


@router.get('/favorites')
async def list_favorites(current_user: dict = Depends(get_current_user)):
    cursor = favorites_collection.find({'user_id': current_user['id']}, {'_id': 0}).sort('created_at', -1)
    return await cursor.to_list(300)


@router.delete('/favorites/{favorite_id}')
async def remove_favorite(favorite_id: str, current_user: dict = Depends(get_current_user)):
    result = await favorites_collection.delete_one({'id': favorite_id, 'user_id': current_user['id']})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail='Favorite not found')
    return {'success': True}


# ---- Documents (auto-registered from research + manual uploads) ----


@router.get('/documents')
async def list_documents(category: str = None, doc_type: str = None, q: str = None,
                          current_user: dict = Depends(get_current_user)):
    query = {}
    if category:
        query['category'] = {'$regex': category, '$options': 'i'}
    if doc_type:
        query['doc_type'] = doc_type
    if q:
        query['title'] = {'$regex': q, '$options': 'i'}
    cursor = documents_collection.find(query, {'_id': 0}).sort('created_at', -1).limit(200)
    return await cursor.to_list(200)


@router.post('/documents')
async def create_document(payload: DocumentCreate, current_user: dict = Depends(require_roles('admin', 'engineer'))):
    doc = payload.model_dump()
    doc['id'] = str(uuid.uuid4())
    doc['source'] = 'manual'
    doc['created_at'] = datetime.now(timezone.utc).isoformat()
    await documents_collection.insert_one(dict(doc))
    return doc


# ---- Categories (fixed enterprise taxonomy - navigation only, no mock product data) ----

CATEGORY_TAXONOMY = {
    'EV Charger': ['EV Connector', 'EVSE Controller', 'Charging Cable', 'RFID Reader', 'Charge Point Controller'],
    'Solar': ['Solar Inverter', 'Solar DC Isolator', 'MC4 Connector', 'Solar Cable', 'Solar Combiner Box'],
    'Electrical Protection': ['MCB', 'MCCB', 'SPD', 'RCD', 'RCCB', 'Fuse'],
    'Switchgear': ['Contactor', 'Relay', 'Circuit Breaker', 'Disconnect Switch'],
    'Communication': ['Energy Meter', 'RS485 Module', 'Modbus Gateway', 'IoT Module'],
    'Power Supply': ['SMPS', 'Power Supply', 'DC-DC Converter', 'UPS'],
    'Accessories': ['Cooling Fan', 'Enclosure', 'Cable Gland', 'Terminal Block'],
}


@router.get('/categories')
async def get_categories(current_user: dict = Depends(get_current_user)):
    return [{'name': k, 'components': v} for k, v in CATEGORY_TAXONOMY.items()]


@router.get('/products')
async def list_products(category: str = None, brand: str = None, q: str = None,
                         current_user: dict = Depends(get_current_user)):
    query = {}
    if category:
        query['category'] = {'$regex': category, '$options': 'i'}
    if brand:
        query['brand'] = {'$regex': brand, '$options': 'i'}
    if q:
        query['name'] = {'$regex': q, '$options': 'i'}
    cursor = products_collection.find(query, {'_id': 0}).sort('engineering_score', -1).limit(100)
    return await cursor.to_list(100)


@router.get('/products/{product_id}')
async def get_product(product_id: str, current_user: dict = Depends(get_current_user)):
    doc = await products_collection.find_one({'id': product_id}, {'_id': 0})
    if not doc:
        raise HTTPException(status_code=404, detail='Product not found')
    return doc


@router.get('/brands')
async def list_brands(current_user: dict = Depends(get_current_user)):
    cursor = brands_collection.find({}, {'_id': 0}).sort('name', 1)
    return await cursor.to_list(300)


# ---- Dashboard ----


@router.get('/dashboard/summary')
async def dashboard_summary(current_user: dict = Depends(get_current_user)):
    recent_searches = await search_history_collection.find(
        {'user_id': current_user['id']}, {'_id': 0}).sort('created_at', -1).limit(5).to_list(5)
    recent_compares = await compare_history_collection.find(
        {'user_id': current_user['id']}, {'_id': 0}).sort('created_at', -1).limit(5).to_list(5)
    favorites_count = await favorites_collection.count_documents({'user_id': current_user['id']})
    total_searches = await search_history_collection.count_documents({'user_id': current_user['id']})
    total_products_researched = await products_collection.count_documents({})

    top_products = await products_collection.find({}, {'_id': 0}).sort('engineering_score', -1).limit(6).to_list(6)

    latest_analyses = await ai_cache_collection.find(
        {}, {'_id': 0, 'id': 1, 'query': 1, 'category': 1, 'summary': 1, 'created_at': 1, 'confidence': 1}
    ).sort('created_at', -1).limit(5).to_list(5)

    return {
        'recent_searches': recent_searches,
        'recent_compares': recent_compares,
        'favorites_count': favorites_count,
        'total_searches': total_searches,
        'total_products_researched': total_products_researched,
        'top_recommended_products': top_products,
        'latest_analyses': latest_analyses,
        'api_status': {
            'tavily_search': settings.tavily_enabled,
            'firecrawl_extract': settings.firecrawl_enabled,
            'ai_analysis': settings.llm_enabled,
        },
        'system_status': 'operational',
    }
