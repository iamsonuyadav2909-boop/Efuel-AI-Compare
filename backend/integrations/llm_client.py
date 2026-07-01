"""
LLM integration via Emergent Universal LLM Key (emergentintegrations library).
Used for structured engineering analysis (JSON) + conversational AI assistant.
Modular: swap provider/model via env vars (LLM_PROVIDER / LLM_MODEL) or later switch
to a direct OpenAI key without changing call sites.
"""
import json
import logging
import re
import uuid
from typing import Optional, List, Dict
from config import settings

logger = logging.getLogger(__name__)


def _extract_json(text: str) -> Optional[dict]:
    """Extract a JSON object from LLM text output, stripping markdown fences if present."""
    if not text:
        return None
    cleaned = text.strip()
    cleaned = re.sub(r'^```(json)?', '', cleaned.strip(), flags=re.IGNORECASE).strip()
    cleaned = re.sub(r'```$', '', cleaned.strip()).strip()
    try:
        return json.loads(cleaned)
    except Exception:
        pass
    # fallback: find first { ... last }
    start = cleaned.find('{')
    end = cleaned.rfind('}')
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(cleaned[start:end + 1])
        except Exception:
            return None
    return None


async def _get_chat(system_message: str, session_id: Optional[str] = None):
    from emergentintegrations.llm.chat import LlmChat
    chat = LlmChat(
        api_key=settings.EMERGENT_LLM_KEY,
        session_id=session_id or str(uuid.uuid4()),
        system_message=system_message,
    ).with_model(settings.LLM_PROVIDER, settings.LLM_MODEL)
    return chat


async def generate_json(system_message: str, user_prompt: str, max_retries: int = 2) -> Optional[dict]:
    """Send a prompt to the LLM and parse a strict JSON response, retrying on parse failure."""
    if not settings.llm_enabled:
        logger.error('LLM disabled: EMERGENT_LLM_KEY not configured')
        return None

    from emergentintegrations.llm.chat import UserMessage

    last_error = None
    for attempt in range(max_retries + 1):
        try:
            chat = await _get_chat(system_message)
            prompt = user_prompt
            if attempt > 0:
                prompt += (
                    "\n\nIMPORTANT: Your previous response was not valid JSON. "
                    "Return ONLY a valid raw JSON object, no markdown fences, no commentary."
                )
            response_text = await chat.send_message(UserMessage(text=prompt))
            parsed = _extract_json(response_text)
            if parsed is not None:
                return parsed
            last_error = 'Could not parse JSON from LLM response'
            logger.warning(f'LLM JSON parse failed on attempt {attempt + 1}')
        except Exception as e:
            last_error = str(e)
            logger.error(f'LLM call error on attempt {attempt + 1}: {e}')

    logger.error(f'LLM generate_json failed after {max_retries + 1} attempts: {last_error}')
    return None


async def generate_chat_reply(system_message: str, session_id: str, message: str) -> str:
    """Conversational reply for the AI Assistant - plain text (markdown allowed)."""
    if not settings.llm_enabled:
        return (
            "AI Assistant is currently unavailable because EMERGENT_LLM_KEY is not configured. "
            "Please contact your administrator."
        )
    try:
        from emergentintegrations.llm.chat import UserMessage
        chat = await _get_chat(system_message, session_id=session_id)
        response_text = await chat.send_message(UserMessage(text=message))
        return response_text
    except Exception as e:
        logger.error(f'LLM chat error: {e}')
        return f"I'm sorry, I encountered an error while processing your request. Please try again shortly."
