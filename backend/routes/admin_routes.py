"""
Admin Panel routes - Users, Roles, Brands, Categories, Products, Documents,
API Integrations, Search Logs, AI Logs, System Settings.

Access control:
    - Catalog/document management (brands, categories, products, documents,
      search/AI logs viewing+clearing): `admin` or `super_admin`.
    - Sensitive system-level actions (user management, API integration keys,
      system settings): `super_admin` only.
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import Response

from auth import require_roles, hash_password
from models_auth import ADMIN_ROLES, ROLE_DEFINITIONS, UserCreate, UserAdminUpdate, PasswordReset
from models_app import (
    BrandCreate, BrandUpdate, ProductCreate, ProductUpdate, DocumentMetadataUpdate,
    IntegrationKeyUpdate, IntegrationToggle, SystemSettingsUpdate,
)
from database import (
    users_collection, brands_collection, categories_collection, products_collection,
    documents_collection, api_logs_collection, search_history_collection,
)
from config import settings
from services import credential_service, storage_service, system_settings_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/admin', tags=['admin'])

admin_dep = require_roles(*ADMIN_ROLES)
super_admin_dep = require_roles('super_admin')

MAX_UPLOAD_BYTES = 20 * 1024 * 1024  # 20MB


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# =====================================================================================
# USERS  (super_admin only - user & role management is a sensitive system action)
# =====================================================================================

@router.get('/users')
async def list_users(current_user: dict = Depends(super_admin_dep)):
    cursor = users_collection.find({}, {'_id': 0, 'password_hash': 0}).sort('created_at', -1)
    return await cursor.to_list(500)


@router.post('/users')
async def create_user(payload: UserCreate, current_user: dict = Depends(super_admin_dep)):
    existing = await users_collection.find_one({'email': payload.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail='A user with this email already exists.')
    doc = {
        'id': str(uuid.uuid4()),
        'name': payload.name,
        'email': payload.email.lower(),
        'password_hash': hash_password(payload.password),
        'role': payload.role,
        'is_active': True,
        'created_at': now_iso(),
    }
    await users_collection.insert_one(dict(doc))
    doc.pop('password_hash', None)
    return doc


@router.put('/users/{user_id}')
async def update_user(user_id: str, payload: UserAdminUpdate, current_user: dict = Depends(super_admin_dep)):
    update = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if not update:
        raise HTTPException(status_code=400, detail='No fields provided to update.')
    if user_id == current_user['id'] and ('role' in update or 'is_active' in update):
        raise HTTPException(status_code=400, detail='You cannot change your own role or active status.')
    if 'email' in update:
        update['email'] = update['email'].lower()
        clash = await users_collection.find_one({'email': update['email'], 'id': {'$ne': user_id}})
        if clash:
            raise HTTPException(status_code=400, detail='Another user already uses this email.')
    result = await users_collection.update_one({'id': user_id}, {'$set': update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail='User not found')
    return {'success': True}


@router.put('/users/{user_id}/role')
async def update_user_role(user_id: str, role: str, current_user: dict = Depends(super_admin_dep)):
    valid_roles = {r['value'] for r in ROLE_DEFINITIONS}
    if role not in valid_roles:
        raise HTTPException(status_code=400, detail='Invalid role')
    if user_id == current_user['id']:
        raise HTTPException(status_code=400, detail='You cannot change your own role.')
    result = await users_collection.update_one({'id': user_id}, {'$set': {'role': role}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail='User not found')
    return {'success': True}


@router.put('/users/{user_id}/status')
async def update_user_status(user_id: str, is_active: bool, current_user: dict = Depends(super_admin_dep)):
    if user_id == current_user['id']:
        raise HTTPException(status_code=400, detail='You cannot disable your own account.')
    result = await users_collection.update_one({'id': user_id}, {'$set': {'is_active': is_active}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail='User not found')
    return {'success': True}


@router.post('/users/{user_id}/reset-password')
async def reset_user_password(user_id: str, payload: PasswordReset, current_user: dict = Depends(super_admin_dep)):
    result = await users_collection.update_one({'id': user_id}, {'$set': {'password_hash': hash_password(payload.new_password)}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail='User not found')
    return {'success': True}


@router.delete('/users/{user_id}')
async def delete_user(user_id: str, current_user: dict = Depends(super_admin_dep)):
    if user_id == current_user['id']:
        raise HTTPException(status_code=400, detail='You cannot delete your own account.')
    result = await users_collection.delete_one({'id': user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail='User not found')
    return {'success': True}


# ---- Roles (informational - powers role dropdowns in the Admin UI) ----

@router.get('/roles')
async def list_roles(current_user: dict = Depends(admin_dep)):
    return ROLE_DEFINITIONS


# =====================================================================================
# BRANDS
# =====================================================================================

@router.get('/brands')
async def admin_list_brands(current_user: dict = Depends(admin_dep)):
    cursor = brands_collection.find({}, {'_id': 0}).sort('name', 1)
    return await cursor.to_list(500)


@router.post('/brands')
async def create_brand(payload: BrandCreate, current_user: dict = Depends(admin_dep)):
    existing = await brands_collection.find_one({'name': payload.name})
    if existing:
        raise HTTPException(status_code=400, detail='A brand with this name already exists.')
    doc = {**payload.model_dump(), 'created_at': now_iso()}
    await brands_collection.insert_one(dict(doc))
    return doc


@router.put('/brands/{brand_name}')
async def update_brand(brand_name: str, payload: BrandUpdate, current_user: dict = Depends(admin_dep)):
    update = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if not update:
        raise HTTPException(status_code=400, detail='No fields provided to update.')
    result = await brands_collection.update_one({'name': brand_name}, {'$set': update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail='Brand not found')
    return {'success': True}


@router.delete('/brands/{brand_name}')
async def delete_brand(brand_name: str, current_user: dict = Depends(admin_dep)):
    await brands_collection.delete_one({'name': brand_name})
    return {'success': True}


# =====================================================================================
# CATEGORIES (custom, in addition to fixed taxonomy)
# =====================================================================================

@router.get('/categories')
async def admin_list_categories(current_user: dict = Depends(admin_dep)):
    cursor = categories_collection.find({}, {'_id': 0}).sort('name', 1)
    return await cursor.to_list(200)


@router.post('/categories')
async def admin_create_category(name: str, current_user: dict = Depends(admin_dep)):
    await categories_collection.update_one(
        {'name': name},
        {'$setOnInsert': {'name': name, 'created_at': now_iso()}},
        upsert=True,
    )
    return {'success': True}


@router.delete('/categories/{name}')
async def admin_delete_category(name: str, current_user: dict = Depends(admin_dep)):
    await categories_collection.delete_one({'name': name})
    return {'success': True}


# =====================================================================================
# PRODUCTS
# =====================================================================================

@router.get('/products')
async def admin_list_products(current_user: dict = Depends(admin_dep)):
    cursor = products_collection.find({}, {'_id': 0}).sort('created_at', -1)
    return await cursor.to_list(500)


@router.post('/products')
async def create_product(payload: ProductCreate, current_user: dict = Depends(admin_dep)):
    doc = {
        'id': str(uuid.uuid4()),
        'name': payload.name,
        'brand': payload.brand,
        'category': payload.category,
        'engineering_score': 0,
        'score_breakdown': {},
        'specifications': payload.specifications,
        'pros': [], 'cons': [],
        'engineering_notes': payload.engineering_notes,
        'compatibility': [], 'industrial_applications': [], 'alternatives': [], 'certifications': [],
        'source_urls': [],
        'ai_recommendation': '',
        'estimated_price_range': payload.estimated_price_range,
        'source': 'manual',
        'created_at': now_iso(),
        'updated_at': now_iso(),
    }
    await products_collection.insert_one(dict(doc))
    await brands_collection.update_one({'name': payload.brand}, {'$setOnInsert': {'name': payload.brand, 'created_at': now_iso()}}, upsert=True)
    return doc


@router.put('/products/{product_id}')
async def update_product(product_id: str, payload: ProductUpdate, current_user: dict = Depends(admin_dep)):
    update = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if not update:
        raise HTTPException(status_code=400, detail='No fields provided to update.')
    update['updated_at'] = now_iso()
    result = await products_collection.update_one({'id': product_id}, {'$set': update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail='Product not found')
    return {'success': True}


@router.delete('/products/{product_id}')
async def delete_product(product_id: str, current_user: dict = Depends(admin_dep)):
    await products_collection.delete_one({'id': product_id})
    return {'success': True}


# =====================================================================================
# DOCUMENTS - complete PDF management system with brand/product libraries + versioning
# =====================================================================================

def _validate_pdf(file: UploadFile, data: bytes):
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail='File too large - maximum size is 20MB.')
    is_pdf = (file.content_type == 'application/pdf') or (file.filename or '').lower().endswith('.pdf')
    if not is_pdf:
        raise HTTPException(status_code=400, detail='Only PDF files are supported.')


async def _upload_single(file: UploadFile, title: str, doc_type: str, category: str,
                          brand: str, product_id: str, product_name: str, uploaded_by: str) -> dict:
    data = await file.read()
    _validate_pdf(file, data)
    path = storage_service.build_path(uploaded_by, file.filename or 'document.pdf')
    try:
        result = await storage_service.put_object(path, data, 'application/pdf')
    except Exception as e:
        logger.error(f'Document upload failed: {e}')
        raise HTTPException(status_code=502, detail=f'Upload to object storage failed: {e}')

    size = result.get('size', len(data))
    version_entry = {
        'version': 1, 'storage_path': path, 'original_filename': file.filename,
        'size': size, 'uploaded_at': now_iso(), 'uploaded_by': uploaded_by,
    }
    doc = {
        'id': str(uuid.uuid4()),
        'title': title or (file.filename or 'Untitled Document').rsplit('.', 1)[0],
        'url': '',
        'doc_type': doc_type or 'datasheet',
        'category': category or '',
        'brand': brand or '',
        'product_id': product_id or '',
        'product_name': product_name or '',
        'source': 'upload',
        'storage_path': path,
        'original_filename': file.filename,
        'content_type': 'application/pdf',
        'size': size,
        'version': 1,
        'versions': [version_entry],
        'is_active': True,
        'is_deleted': False,
        'uploaded_by': uploaded_by,
        'created_at': now_iso(),
        'updated_at': now_iso(),
    }
    await documents_collection.insert_one(dict(doc))
    doc.pop('_id', None)
    return doc


@router.get('/documents')
async def admin_list_documents(brand: Optional[str] = None, product_id: Optional[str] = None,
                                is_active: Optional[bool] = None, include_deleted: bool = False,
                                current_user: dict = Depends(admin_dep)):
    query = {}
    if not include_deleted:
        query['is_deleted'] = {'$ne': True}
    if brand:
        query['brand'] = brand
    if product_id:
        query['product_id'] = product_id
    if is_active is not None:
        query['is_active'] = is_active
    cursor = documents_collection.find(query, {'_id': 0}).sort('created_at', -1)
    return await cursor.to_list(500)


@router.post('/documents/upload')
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(''),
    doc_type: str = Form('datasheet'),
    category: str = Form(''),
    brand: str = Form(''),
    product_id: str = Form(''),
    product_name: str = Form(''),
    current_user: dict = Depends(admin_dep),
):
    return await _upload_single(file, title, doc_type, category, brand, product_id, product_name, current_user['id'])


@router.post('/documents/bulk-upload')
async def bulk_upload_documents(
    files: List[UploadFile] = File(...),
    doc_type: str = Form('datasheet'),
    category: str = Form(''),
    brand: str = Form(''),
    product_id: str = Form(''),
    product_name: str = Form(''),
    current_user: dict = Depends(admin_dep),
):
    created, errors = [], []
    for f in files:
        try:
            doc = await _upload_single(f, '', doc_type, category, brand, product_id, product_name, current_user['id'])
            created.append(doc)
        except HTTPException as e:
            errors.append({'filename': f.filename, 'error': e.detail})
        except Exception as e:
            errors.append({'filename': f.filename, 'error': str(e)})
    return {'created': created, 'errors': errors}


@router.post('/documents/{document_id}/replace')
async def replace_document(document_id: str, file: UploadFile = File(...), current_user: dict = Depends(admin_dep)):
    doc = await documents_collection.find_one({'id': document_id}, {'_id': 0})
    if not doc:
        raise HTTPException(status_code=404, detail='Document not found')
    data = await file.read()
    _validate_pdf(file, data)
    path = storage_service.build_path(current_user['id'], file.filename or 'document.pdf')
    try:
        result = await storage_service.put_object(path, data, 'application/pdf')
    except Exception as e:
        logger.error(f'Document replace failed: {e}')
        raise HTTPException(status_code=502, detail=f'Upload to object storage failed: {e}')

    new_version = (doc.get('version') or 1) + 1
    size = result.get('size', len(data))
    version_entry = {
        'version': new_version, 'storage_path': path, 'original_filename': file.filename,
        'size': size, 'uploaded_at': now_iso(), 'uploaded_by': current_user['id'],
    }
    versions = doc.get('versions') or []
    versions.append(version_entry)
    await documents_collection.update_one(
        {'id': document_id},
        {'$set': {
            'storage_path': path, 'original_filename': file.filename, 'content_type': 'application/pdf',
            'size': size, 'version': new_version, 'versions': versions, 'source': 'upload',
            'updated_at': now_iso(),
        }},
    )
    return {'success': True, 'version': new_version}


@router.get('/documents/{document_id}/versions')
async def document_versions(document_id: str, current_user: dict = Depends(admin_dep)):
    doc = await documents_collection.find_one({'id': document_id}, {'_id': 0, 'versions': 1})
    if not doc:
        raise HTTPException(status_code=404, detail='Document not found')
    return doc.get('versions', [])


@router.put('/documents/{document_id}')
async def update_document_metadata(document_id: str, payload: DocumentMetadataUpdate, current_user: dict = Depends(admin_dep)):
    update = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if not update:
        raise HTTPException(status_code=400, detail='No fields provided to update.')
    update['updated_at'] = now_iso()
    result = await documents_collection.update_one({'id': document_id}, {'$set': update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail='Document not found')
    return {'success': True}


@router.put('/documents/{document_id}/status')
async def toggle_document_status(document_id: str, is_active: bool, current_user: dict = Depends(admin_dep)):
    result = await documents_collection.update_one({'id': document_id}, {'$set': {'is_active': is_active, 'updated_at': now_iso()}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail='Document not found')
    return {'success': True}


@router.delete('/documents/{document_id}')
async def delete_document(document_id: str, current_user: dict = Depends(admin_dep)):
    result = await documents_collection.update_one(
        {'id': document_id},
        {'$set': {'is_deleted': True, 'is_active': False, 'updated_at': now_iso()}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail='Document not found')
    return {'success': True}


@router.post('/documents/bulk-delete')
async def bulk_delete_documents(ids: List[str], current_user: dict = Depends(admin_dep)):
    result = await documents_collection.update_many(
        {'id': {'$in': ids}},
        {'$set': {'is_deleted': True, 'is_active': False, 'updated_at': now_iso()}},
    )
    return {'success': True, 'modified_count': result.modified_count}


# =====================================================================================
# SEARCH LOGS  (user search_history - includes "clear/clean" rights)
# =====================================================================================

@router.get('/search-logs')
async def list_search_logs(limit: int = Query(200, le=1000), current_user: dict = Depends(admin_dep)):
    cursor = search_history_collection.find({}, {'_id': 0}).sort('created_at', -1).limit(limit)
    return await cursor.to_list(limit)


@router.delete('/search-logs/{log_id}')
async def delete_search_log(log_id: str, current_user: dict = Depends(admin_dep)):
    result = await search_history_collection.delete_one({'id': log_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail='Search log entry not found')
    return {'success': True}


@router.delete('/search-logs')
async def clear_search_logs(current_user: dict = Depends(admin_dep)):
    result = await search_history_collection.delete_many({})
    return {'success': True, 'deleted_count': result.deleted_count}


# =====================================================================================
# AI LOGS  (pipeline stage logs: search / firecrawl_extract / llm_analyze / no_data_gate)
# =====================================================================================

@router.get('/logs')
async def admin_logs(stage: Optional[str] = None, limit: int = Query(100, le=1000), current_user: dict = Depends(admin_dep)):
    query = {}
    if stage:
        query['stage'] = stage
    cursor = api_logs_collection.find(query, {'_id': 0}).sort('created_at', -1).limit(limit)
    return await cursor.to_list(limit)


@router.delete('/logs')
async def clear_ai_logs(current_user: dict = Depends(super_admin_dep)):
    result = await api_logs_collection.delete_many({})
    return {'success': True, 'deleted_count': result.deleted_count}


# =====================================================================================
# API INTEGRATIONS  (super_admin only - encrypted keys, enable/disable, test connection)
# =====================================================================================

@router.get('/api-keys/status')
async def api_keys_status(current_user: dict = Depends(admin_dep)):
    status = await credential_service.get_all_status()
    return {
        'exa': {**status['exa'], 'env_var': 'EXA_API_KEY',
                'description': 'PRIMARY semantic search for manufacturer datasheets, specs & pricing'},
        'tavily': {**status['tavily'], 'env_var': 'TAVILY_API_KEY',
                   'description': 'Fallback web search for manufacturer sources (used if Exa unavailable)'},
        'firecrawl': {**status['firecrawl'], 'env_var': 'FIRECRAWL_API_KEY',
                      'description': 'Extracts specs/datasheets from manufacturer pages'},
        'emergent_llm': {**status['emergent_llm'], 'env_var': 'EMERGENT_LLM_KEY',
                         'provider': settings.LLM_PROVIDER, 'model': settings.LLM_MODEL,
                         'description': 'Structures & scores verified live data - chat assistant, compare & BOM engine'},
    }


@router.get('/integrations')
async def list_integrations(current_user: dict = Depends(super_admin_dep)):
    return await credential_service.get_all_status()


@router.put('/integrations/{provider}/key')
async def update_integration_key(provider: str, payload: IntegrationKeyUpdate, current_user: dict = Depends(super_admin_dep)):
    if provider not in credential_service.ENV_FALLBACKS:
        raise HTTPException(status_code=404, detail='Unknown integration provider')
    ok = await credential_service.set_api_key(provider, payload.api_key, payload.enabled)
    if not ok:
        raise HTTPException(status_code=500, detail='Could not save key - CREDENTIAL_ENCRYPTION_KEY missing/invalid on server.')
    return {'success': True}


@router.put('/integrations/{provider}/toggle')
async def toggle_integration(provider: str, payload: IntegrationToggle, current_user: dict = Depends(super_admin_dep)):
    if provider not in credential_service.ENV_FALLBACKS:
        raise HTTPException(status_code=404, detail='Unknown integration provider')
    await credential_service.set_provider_enabled(provider, payload.enabled)
    return {'success': True}


@router.post('/integrations/{provider}/test')
async def test_integration(provider: str, current_user: dict = Depends(super_admin_dep)):
    if provider == 'exa':
        from integrations.exa_client import search_exa_sources
        data = await search_exa_sources('MCB circuit breaker', max_results=1)
        if not data.get('enabled'):
            return {'success': False, 'message': 'Exa is not configured (no API key resolvable).'}
        if data.get('error'):
            return {'success': False, 'message': f'Exa error: {data["error"]}'}
        return {'success': True, 'message': f'Exa responded with {len(data.get("results", []))} result(s).'}

    if provider == 'tavily':
        from integrations.tavily_client import search_trusted_sources
        data = await search_trusted_sources('MCB circuit breaker', max_results=1)
        if not data.get('enabled'):
            return {'success': False, 'message': 'Tavily is not configured (no API key resolvable).'}
        if data.get('error'):
            return {'success': False, 'message': f'Tavily error: {data["error"]}'}
        return {'success': True, 'message': f'Tavily responded with {len(data.get("results", []))} result(s).'}

    if provider == 'firecrawl':
        from integrations.firecrawl_client import extract_pages
        data = await extract_pages(['https://example.com'], max_pages=1)
        if not data.get('enabled'):
            return {'success': False, 'message': 'Firecrawl is not configured (no API key resolvable).'}
        if not data.get('pages'):
            return {'success': False, 'message': f'Firecrawl could not scrape the test page: {data.get("error", "unknown error")}'}
        return {'success': True, 'message': 'Firecrawl successfully scraped a test page.'}

    if provider == 'emergent_llm':
        from integrations.llm_client import generate_json
        result = await generate_json(
            'You are a connectivity test assistant. Always respond with valid raw JSON only.',
            'Return exactly this JSON object: {"status": "ok"}',
            max_retries=1,
        )
        if not result:
            return {'success': False, 'message': 'Emergent LLM key is not configured or the call failed.'}
        return {'success': True, 'message': 'Emergent LLM responded successfully.'}

    raise HTTPException(status_code=404, detail='Unknown integration provider')


# =====================================================================================
# SYSTEM SETTINGS  (super_admin only)
# =====================================================================================

@router.get('/settings')
async def get_system_settings(current_user: dict = Depends(super_admin_dep)):
    return await system_settings_service.get_settings()


@router.put('/settings')
async def update_system_settings(payload: SystemSettingsUpdate, current_user: dict = Depends(super_admin_dep)):
    return await system_settings_service.update_settings(payload.model_dump(exclude_unset=True))
