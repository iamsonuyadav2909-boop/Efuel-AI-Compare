"""
System-wide, Admin-configurable settings for EFUEL Engineering Hub - stored in
MongoDB (`system_settings` collection) so they can be changed live from the
Admin Panel without redeploying. Falls back to `.env`-derived defaults from
`config.settings` when nothing has been configured yet.

This is the concrete mechanism behind the "future-ready, pluggable AI provider"
requirement: `llm_provider` / `llm_model` here are read by `integrations/llm_client.py`
on every call, so switching from Emergent's OpenAI model to Anthropic/Google (all
still billed through the same EMERGENT_LLM_KEY) requires only an Admin Panel update.
"""
import logging
from typing import Optional

from config import settings
from database import system_settings_collection

logger = logging.getLogger(__name__)

SETTINGS_DOC_ID = 'global'


def _defaults() -> dict:
    return {
        'llm_provider': settings.LLM_PROVIDER,
        'llm_model': settings.LLM_MODEL,
        'research_rate_limit_per_min': 15,
    }


async def get_settings() -> dict:
    doc = await system_settings_collection.find_one({'_key': SETTINGS_DOC_ID}, {'_id': 0, '_key': 0})
    merged = {**_defaults(), **(doc or {})}
    return merged


async def update_settings(update: dict) -> dict:
    clean = {k: v for k, v in update.items() if v is not None}
    if clean:
        from datetime import datetime, timezone
        clean['updated_at'] = datetime.now(timezone.utc).isoformat()
        await system_settings_collection.update_one(
            {'_key': SETTINGS_DOC_ID},
            {'$set': clean, '$setOnInsert': {'_key': SETTINGS_DOC_ID}},
            upsert=True,
        )
    return await get_settings()


async def get_llm_provider_model() -> tuple:
    s = await get_settings()
    return s.get('llm_provider') or settings.LLM_PROVIDER, s.get('llm_model') or settings.LLM_MODEL
