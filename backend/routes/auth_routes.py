"""Authentication routes: single-account login only. Public self-registration is
disabled by design - EFUEL Engineering Hub is a private internal tool with exactly
one owner-managed credential (see backend/scripts/seed_users.py)."""
from fastapi import APIRouter, HTTPException, Depends

from models_auth import UserLogin, UserPublic, TokenResponse
from auth import verify_password, create_access_token, get_current_user
from database import users_collection

router = APIRouter(prefix='/auth', tags=['auth'])


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
