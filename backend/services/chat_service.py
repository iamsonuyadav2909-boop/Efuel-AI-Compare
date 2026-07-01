"""
AI Assistant (chat) service - grounded in cached research results (Tavily/Firecrawl/LLM data)
stored in the ai_cache collection, per the core research workflow.
"""
import logging
from datetime import datetime, timezone

from database import ai_cache_collection, chat_sessions_collection
from integrations.llm_client import generate_chat_reply

logger = logging.getLogger(__name__)

CHAT_SYSTEM_MESSAGE = (
    "You are the EFUEL Engineering Assistant, an expert in EV charging and solar electrical "
    "components (MCB, MCCB, SPD, Contactors, Relays, Energy Meters, Solar Inverters, DC Isolators, "
    "MC4, Solar Cables, EV Connectors, SMPS, Power Supplies, Enclosures, etc). Answer engineering "
    "questions clearly, concisely and helpfully, referencing real brands/models. When CACHED RESEARCH "
    "DATA is provided below, use it as grounding context. Respond in natural, well-formatted markdown "
    "text (not JSON). Keep answers focused and practical for a working engineer or procurement lead."
)


async def _get_relevant_context(message: str, limit: int = 3) -> str:
    words = [w.strip('?.,!') for w in message.lower().split() if len(w.strip('?.,!')) > 2][:8]
    if not words:
        return ''
    try:
        cursor = ai_cache_collection.find(
            {'$or': [{'query': {'$regex': w, '$options': 'i'}} for w in words]},
            {'_id': 0, 'query': 1, 'category': 1, 'summary': 1, 'top_recommendation': 1},
        ).sort('created_at', -1).limit(limit)
        docs = await cursor.to_list(limit)
        if not docs:
            return ''
        parts = [
            f"- Query '{d.get('query','')}' ({d.get('category','')}): {d.get('summary','')} "
            f"Top pick: {d.get('top_recommendation','')}"
            for d in docs
        ]
        return "CACHED RESEARCH DATA:\n" + "\n".join(parts)
    except Exception as e:
        logger.warning(f'Chat context lookup failed: {e}')
        return ''


async def chat_reply(message: str, session_id: str, user_id: str) -> str:
    context = await _get_relevant_context(message)
    full_message = f"{context}\n\nUser question: {message}" if context else message
    reply = await generate_chat_reply(CHAT_SYSTEM_MESSAGE, session_id, full_message)

    now = datetime.now(timezone.utc).isoformat()
    await chat_sessions_collection.update_one(
        {'session_id': session_id, 'user_id': user_id},
        {
            '$push': {'messages': {'$each': [
                {'role': 'user', 'content': message, 'created_at': now},
                {'role': 'assistant', 'content': reply, 'created_at': now},
            ]}},
            '$setOnInsert': {'session_id': session_id, 'user_id': user_id, 'created_at': now},
            '$set': {'updated_at': now},
        },
        upsert=True,
    )
    return reply
