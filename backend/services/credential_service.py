"""
Encrypted API credential management for EFUEL Engineering Hub.

Resolves API keys with this strict priority:
    1) Admin-configured, encrypted key stored in MongoDB (`integration_credentials`)
    2) Environment variable fallback (`backend/.env`)

This allows an Admin to add/rotate/disable Exa, Tavily, Firecrawl, Emergent LLM (and
any future provider) credentials live from the Admin Panel (Phase B) without ever
restarting or redeploying the application. Keys are encrypted at rest using Fernet
(symmetric encryption) with `CREDENTIAL_ENCRYPTION_KEY`.

Also tracks lightweight health/usage telemetry (last success, last error, usage
count) per provider so the future "AI Integrations" Admin dashboard can display
real, non-mocked status without any extra plumbing.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

from config import settings
from database import db

logger = logging.getLogger(__name__)

integration_credentials_collection = db['integration_credentials']

# Human-friendly labels + env-var fallback getters for every known provider.
# Adding a future provider (Google CSE, SerpAPI, OpenAI direct, etc.) only
# requires registering it here - no other code needs to change.
PROVIDER_LABELS = {
    'exa': 'Exa Search',
    'tavily': 'Tavily Search',
    'firecrawl': 'Firecrawl',
    'emergent_llm': 'Emergent LLM',
}

ENV_FALLBACKS = {
    'exa': lambda: settings.EXA_API_KEY,
    'tavily': lambda: settings.TAVILY_API_KEY,
    'firecrawl': lambda: settings.FIRECRAWL_API_KEY,
    'emergent_llm': lambda: settings.EMERGENT_LLM_KEY,
}


def _fernet() -> Optional[Fernet]:
    key = (settings.CREDENTIAL_ENCRYPTION_KEY or '').strip()
    if not key:
        return None
    try:
        return Fernet(key.encode('utf-8'))
    except Exception as e:
        logger.error(f'Invalid CREDENTIAL_ENCRYPTION_KEY, cannot use Mongo-stored credentials: {e}')
        return None


def encrypt_value(raw: str) -> Optional[str]:
    f = _fernet()
    if not f or not raw:
        return None
    return f.encrypt(raw.encode('utf-8')).decode('utf-8')


def decrypt_value(token: str) -> Optional[str]:
    f = _fernet()
    if not f or not token:
        return None
    try:
        return f.decrypt(token.encode('utf-8')).decode('utf-8')
    except (InvalidToken, Exception) as e:
        logger.error(f'Failed to decrypt stored credential: {e}')
        return None


async def get_credential_doc(provider: str) -> Optional[dict]:
    return await integration_credentials_collection.find_one({'provider': provider}, {'_id': 0})


async def get_api_key(provider: str) -> Optional[str]:
    """Resolve the active API key for a provider: Mongo (admin-configured, encrypted,
    enabled) takes priority; falls back to the environment variable."""
    doc = await get_credential_doc(provider)
    if doc and doc.get('enabled', True) and doc.get('encrypted_key'):
        decrypted = decrypt_value(doc['encrypted_key'])
        if decrypted:
            return decrypted
    env_getter = ENV_FALLBACKS.get(provider)
    if env_getter:
        env_val = (env_getter() or '').strip()
        if env_val:
            return env_val
    return None


async def is_provider_configured(provider: str) -> bool:
    return bool(await get_api_key(provider))


async def set_api_key(provider: str, raw_key: str, enabled: bool = True) -> bool:
    """Admin action: store a new encrypted key for a provider in MongoDB."""
    now_iso = datetime.now(timezone.utc).isoformat()
    update = {
        'enabled': enabled,
        'updated_at': now_iso,
        'provider_label': PROVIDER_LABELS.get(provider, provider),
    }
    if raw_key:
        encrypted = encrypt_value(raw_key)
        if encrypted is None:
            logger.error(f'Could not encrypt key for {provider}: CREDENTIAL_ENCRYPTION_KEY missing/invalid')
            return False
        update['encrypted_key'] = encrypted
        update['has_key'] = True
    await integration_credentials_collection.update_one(
        {'provider': provider},
        {'$set': update, '$setOnInsert': {'provider': provider, 'created_at': now_iso, 'usage_count': 0}},
        upsert=True,
    )
    return True


async def set_provider_enabled(provider: str, enabled: bool) -> bool:
    await integration_credentials_collection.update_one(
        {'provider': provider},
        {
            '$set': {'enabled': enabled, 'updated_at': datetime.now(timezone.utc).isoformat()},
            '$setOnInsert': {'provider': provider, 'created_at': datetime.now(timezone.utc).isoformat(), 'usage_count': 0},
        },
        upsert=True,
    )
    return True


async def record_success(provider: str):
    try:
        await integration_credentials_collection.update_one(
            {'provider': provider},
            {
                '$set': {'last_success_at': datetime.now(timezone.utc).isoformat(), 'last_error': None},
                '$inc': {'usage_count': 1},
                '$setOnInsert': {'provider': provider, 'enabled': True, 'created_at': datetime.now(timezone.utc).isoformat()},
            },
            upsert=True,
        )
    except Exception as e:
        logger.error(f'Failed to record success telemetry for {provider}: {e}')


async def record_error(provider: str, error: str):
    try:
        await integration_credentials_collection.update_one(
            {'provider': provider},
            {
                '$set': {'last_error': error[:500], 'last_error_at': datetime.now(timezone.utc).isoformat()},
                '$setOnInsert': {'provider': provider, 'enabled': True, 'created_at': datetime.now(timezone.utc).isoformat(), 'usage_count': 0},
            },
            upsert=True,
        )
    except Exception as e:
        logger.error(f'Failed to record error telemetry for {provider}: {e}')


async def get_all_status() -> dict:
    """Aggregated status for every known provider - used by dashboard + Admin Panel."""
    result = {}
    for provider in ENV_FALLBACKS.keys():
        doc = await get_credential_doc(provider) or {}
        env_val = (ENV_FALLBACKS[provider]() or '').strip()
        mongo_configured = bool(doc.get('encrypted_key'))
        enabled = doc.get('enabled', True)
        configured = (mongo_configured or bool(env_val)) and enabled
        result[provider] = {
            'label': PROVIDER_LABELS.get(provider, provider),
            'configured': configured,
            'enabled': enabled,
            'source': 'admin_configured' if mongo_configured else ('env' if env_val else None),
            'last_success_at': doc.get('last_success_at'),
            'last_error': doc.get('last_error'),
            'last_error_at': doc.get('last_error_at'),
            'usage_count': doc.get('usage_count', 0),
            'updated_at': doc.get('updated_at'),
        }
    return result
