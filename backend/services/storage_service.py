"""
Emergent Object Storage integration - used by the PDF Document Management System
(Admin Panel -> Documents tab) to store uploaded datasheets/catalogues/manuals.

Uses the Emergent-provided S3-compatible storage API (authenticated via the
existing EMERGENT_LLM_KEY - no additional credentials required from the user).

Constraints (per Emergent Object Storage):
    - No delete API -> soft-delete is implemented at the application/DB layer
      (`documents_collection` `is_deleted` flag is the source of truth).
    - No rename API -> replacing a file uploads to a NEW path and the DB
      reference / version history is updated accordingly.
    - No presigned URLs -> all file access is proxied through our own backend
      endpoints (see routes/misc_routes.py `GET /documents/{id}/file`).
"""
import logging
import uuid
from typing import Optional, Tuple

import httpx

from config import settings

logger = logging.getLogger(__name__)

STORAGE_API_BASE = "https://integrations.emergentagent.com/objstore/api/v1/storage"
APP_NAME = "efuel-engineering-hub"

_storage_key: Optional[str] = None


async def init_storage() -> Optional[str]:
    """Initialize (once) and cache the session-scoped storage key. Safe to call
    repeatedly - subsequent calls are no-ops once initialized. Returns None (and
    logs) if initialization fails, so upload attempts can fail gracefully rather
    than crashing the app at startup."""
    global _storage_key
    if _storage_key:
        return _storage_key
    if not settings.EMERGENT_LLM_KEY:
        logger.warning('Object storage not initialized: EMERGENT_LLM_KEY not configured')
        return None
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(f"{STORAGE_API_BASE}/init", json={"emergent_key": settings.EMERGENT_LLM_KEY})
            resp.raise_for_status()
            _storage_key = resp.json()["storage_key"]
            logger.info('Object storage initialized successfully')
            return _storage_key
    except Exception as e:
        logger.error(f'Object storage initialization failed: {e}')
        return None


def build_path(scope: str, filename: str) -> str:
    """Build a collision-free storage path for a new upload.
    `scope` is typically the uploading user's id (isolates files logically)."""
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'bin'
    return f"{APP_NAME}/documents/{scope}/{uuid.uuid4()}.{ext}"


async def put_object(path: str, data: bytes, content_type: str) -> dict:
    """Upload bytes to storage. Returns {"path", "size", "etag"} on success."""
    key = await init_storage()
    if not key:
        raise RuntimeError('Object storage is not available (EMERGENT_LLM_KEY missing/invalid)')
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.put(
            f"{STORAGE_API_BASE}/objects/{path}",
            headers={"X-Storage-Key": key, "Content-Type": content_type},
            content=data,
        )
        resp.raise_for_status()
        return resp.json()


async def get_object(path: str) -> Tuple[bytes, str]:
    """Download bytes from storage. Returns (content_bytes, content_type)."""
    key = await init_storage()
    if not key:
        raise RuntimeError('Object storage is not available (EMERGENT_LLM_KEY missing/invalid)')
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get(f"{STORAGE_API_BASE}/objects/{path}", headers={"X-Storage-Key": key})
        resp.raise_for_status()
        return resp.content, resp.headers.get('Content-Type', 'application/octet-stream')
