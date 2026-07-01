"""
JWT authentication utilities + FastAPI dependencies for EFUEL Engineering Hub.
Roles: super_admin, admin, engineer, procurement, viewer (see models_auth.py).
"""
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import settings
from database import users_collection

security = HTTPBearer()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False


def create_access_token(user_id: str, email: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {'sub': user_id, 'email': email, 'role': role, 'exp': expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Session expired. Please log in again.')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid authentication token.')


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    payload = decode_token(credentials.credentials)
    user = await users_collection.find_one({'id': payload['sub']}, {'_id': 0, 'password_hash': 0})
    if not user:
        raise HTTPException(status_code=401, detail='User not found')
    if not user.get('is_active', True):
        raise HTTPException(status_code=403, detail='Account disabled. Contact your administrator.')
    return user


def require_roles(*roles):
    async def checker(user: dict = Depends(get_current_user)) -> dict:
        if user['role'] not in roles:
            raise HTTPException(status_code=403, detail='Insufficient permissions for this action.')
        return user
    return checker
