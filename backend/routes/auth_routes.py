"""Authentication routes: register, login, current user."""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
import uuid

from models_auth import UserCreate, UserLogin, UserPublic, TokenResponse
from auth import hash_password, verify_password, create_access_token, get_current_user
from database import users_collection

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', response_model=TokenResponse)
async def register(payload: UserCreate):
    existing = await users_collection.find_one({'email': payload.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail='An account with this email already exists.')
    user_id = str(uuid.uuid4())
    doc = {
        'id': user_id,
        'name': payload.name,
        'email': payload.email.lower(),
        'password_hash': hash_password(payload.password),
        'role': payload.role,
        'is_active': True,
        'created_at': datetime.now(timezone.utc).isoformat(),
    }
    await users_collection.insert_one(doc)
    token = create_access_token(user_id, doc['email'], doc['role'])
    user_public = UserPublic(id=user_id, name=doc['name'], email=doc['email'], role=doc['role'],
                              is_active=True, created_at=doc['created_at'])
    return TokenResponse(access_token=token, user=user_public)


@router.post('/login', response_model=TokenResponse)
async def login(payload: UserLogin):
    user = await users_collection.find_one({'email': payload.email.lower()})
    if not user or not verify_password(payload.password, user['password_hash']):
        raise HTTPException(status_code=401, detail='Invalid email or password.')
    if not user.get('is_active', True):
        raise HTTPException(status_code=403, detail='Account disabled. Contact your administrator.')
    token = create_access_token(user['id'], user['email'], user['role'])
    user_public = UserPublic(id=user['id'], name=user['name'], email=user['email'], role=user['role'],
                              is_active=user.get('is_active', True), created_at=user.get('created_at'))
    return TokenResponse(access_token=token, user=user_public)


@router.get('/me', response_model=UserPublic)
async def me(current_user: dict = Depends(get_current_user)):
    return UserPublic(**current_user)
