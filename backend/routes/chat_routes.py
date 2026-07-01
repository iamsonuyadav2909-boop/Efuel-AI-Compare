"""AI Assistant (chat) routes."""
from fastapi import APIRouter, Depends, HTTPException
import uuid

from models_app import ChatRequest
from services.chat_service import chat_reply
from auth import get_current_user
from database import chat_sessions_collection
from utils import check_rate_limit

router = APIRouter(prefix='/chat', tags=['chat'])


@router.post('')
async def chat(payload: ChatRequest, current_user: dict = Depends(get_current_user)):
    check_rate_limit(f"chat:{current_user['id']}", max_requests=30, window_seconds=60)
    session_id = payload.session_id or str(uuid.uuid4())
    try:
        reply = await chat_reply(payload.message, session_id, current_user['id'])
    except Exception as e:
        raise HTTPException(status_code=502, detail=f'AI Assistant error: {e}')
    return {'session_id': session_id, 'reply': reply}


@router.get('/sessions')
async def list_sessions(current_user: dict = Depends(get_current_user)):
    cursor = chat_sessions_collection.find({'user_id': current_user['id']}, {'_id': 0}) \
        .sort('updated_at', -1).limit(30)
    return await cursor.to_list(30)


@router.get('/sessions/{session_id}')
async def get_session(session_id: str, current_user: dict = Depends(get_current_user)):
    doc = await chat_sessions_collection.find_one(
        {'session_id': session_id, 'user_id': current_user['id']}, {'_id': 0}
    )
    if not doc:
        return {'session_id': session_id, 'messages': []}
    return doc
