"""Admin Panel routes - Users, Brands, Categories, Products, Documents, Logs, API Key status.
All routes require admin role.
"""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone

from auth import require_roles
from database import (
    users_collection, brands_collection, categories_collection, products_collection,
    documents_collection, api_logs_collection,
)
from config import settings

router = APIRouter(prefix='/admin', tags=['admin'])


# ---- Users ----
@router.get('/users')
async def list_users(current_user: dict = Depends(require_roles('admin'))):
    cursor = users_collection.find({}, {'_id': 0, 'password_hash': 0}).sort('created_at', -1)
    return await cursor.to_list(500)


@router.put('/users/{user_id}/role')
async def update_user_role(user_id: str, role: str, current_user: dict = Depends(require_roles('admin'))):
    if role not in ('admin', 'engineer', 'viewer'):
        raise HTTPException(status_code=400, detail='Invalid role')
    if user_id == current_user['id']:
        raise HTTPException(status_code=400, detail='You cannot change your own role.')
    result = await users_collection.update_one({'id': user_id}, {'$set': {'role': role}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail='User not found')
    return {'success': True}


@router.put('/users/{user_id}/status')
async def update_user_status(user_id: str, is_active: bool, current_user: dict = Depends(require_roles('admin'))):
    if user_id == current_user['id']:
        raise HTTPException(status_code=400, detail='You cannot disable your own account.')
    result = await users_collection.update_one({'id': user_id}, {'$set': {'is_active': is_active}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail='User not found')
    return {'success': True}


# ---- Brands ----
@router.get('/brands')
async def admin_list_brands(current_user: dict = Depends(require_roles('admin'))):
    cursor = brands_collection.find({}, {'_id': 0}).sort('name', 1)
    return await cursor.to_list(500)


@router.delete('/brands/{brand_name}')
async def delete_brand(brand_name: str, current_user: dict = Depends(require_roles('admin'))):
    await brands_collection.delete_one({'name': brand_name})
    return {'success': True}


# ---- Categories (custom, in addition to fixed taxonomy) ----
@router.get('/categories')
async def admin_list_categories(current_user: dict = Depends(require_roles('admin'))):
    cursor = categories_collection.find({}, {'_id': 0}).sort('name', 1)
    return await cursor.to_list(200)


@router.post('/categories')
async def admin_create_category(name: str, current_user: dict = Depends(require_roles('admin'))):
    await categories_collection.update_one(
        {'name': name},
        {'$setOnInsert': {'name': name, 'created_at': datetime.now(timezone.utc).isoformat()}},
        upsert=True,
    )
    return {'success': True}


@router.delete('/categories/{name}')
async def admin_delete_category(name: str, current_user: dict = Depends(require_roles('admin'))):
    await categories_collection.delete_one({'name': name})
    return {'success': True}


# ---- Products ----
@router.get('/products')
async def admin_list_products(current_user: dict = Depends(require_roles('admin'))):
    cursor = products_collection.find({}, {'_id': 0}).sort('created_at', -1)
    return await cursor.to_list(500)


@router.delete('/products/{product_id}')
async def delete_product(product_id: str, current_user: dict = Depends(require_roles('admin'))):
    await products_collection.delete_one({'id': product_id})
    return {'success': True}


# ---- Documents ----
@router.get('/documents')
async def admin_list_documents(current_user: dict = Depends(require_roles('admin'))):
    cursor = documents_collection.find({}, {'_id': 0}).sort('created_at', -1)
    return await cursor.to_list(500)


@router.delete('/documents/{document_id}')
async def delete_document(document_id: str, current_user: dict = Depends(require_roles('admin'))):
    await documents_collection.delete_one({'id': document_id})
    return {'success': True}


# ---- Logs ----
@router.get('/logs')
async def admin_logs(stage: str = None, limit: int = 100, current_user: dict = Depends(require_roles('admin'))):
    query = {}
    if stage:
        query['stage'] = stage
    cursor = api_logs_collection.find(query, {'_id': 0}).sort('created_at', -1).limit(limit)
    return await cursor.to_list(limit)


# ---- API Key / Integration status ----
@router.get('/api-keys/status')
async def api_keys_status(current_user: dict = Depends(require_roles('admin'))):
    return {
        'tavily': {'configured': settings.tavily_enabled, 'env_var': 'TAVILY_API_KEY',
                   'description': 'Trusted web search for manufacturer sources'},
        'firecrawl': {'configured': settings.firecrawl_enabled, 'env_var': 'FIRECRAWL_API_KEY',
                      'description': 'Extracts specs/datasheets from manufacturer pages'},
        'emergent_llm': {'configured': settings.llm_enabled, 'env_var': 'EMERGENT_LLM_KEY',
                         'provider': settings.LLM_PROVIDER, 'model': settings.LLM_MODEL,
                         'description': 'AI analysis, ranking, chat assistant, BOM & compare engine'},
    }
