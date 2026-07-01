"""
Sets up the SINGLE owner credential for EFUEL Engineering Hub.

This is a private internal tool - there is no public self-registration and no
multi-user directory. Running this script wipes any existing accounts and creates
exactly ONE admin credential (full access to every module, including Admin Panel).

Run with: python scripts/seed_users.py
Safe to re-run - it always resets to the one credential defined below.
"""
import asyncio
import sys
import os
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import users_collection, close_db
from auth import hash_password

# The one and only owner credential for this deployment.
OWNER_EMAIL = 'owner@efuelhub.com'
OWNER_PASSWORD = 'EfuelOwner@2026!'
OWNER_NAME = 'EFUEL Owner'


async def seed():
    deleted = await users_collection.delete_many({})
    print(f'Removed {deleted.deleted_count} existing account(s).')

    doc = {
        'id': str(uuid.uuid4()),
        'name': OWNER_NAME,
        'email': OWNER_EMAIL.lower(),
        'password_hash': hash_password(OWNER_PASSWORD),
        'role': 'admin',
        'is_active': True,
        'created_at': datetime.now(timezone.utc).isoformat(),
    }
    await users_collection.insert_one(doc)
    print(f'Created single owner account: {OWNER_EMAIL} / {OWNER_PASSWORD} (role=admin)')
    await close_db()


if __name__ == '__main__':
    asyncio.run(seed())
