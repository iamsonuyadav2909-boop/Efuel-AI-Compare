"""
Seed default test users (Admin / Engineer / Viewer) for EFUEL Engineering Hub.
Run with: python scripts/seed_users.py
Safe to re-run (idempotent - skips existing users).
"""
import asyncio
import sys
import os
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import users_collection, close_db
from auth import hash_password

TEST_USERS = [
    {'name': 'Admin User', 'email': 'admin@efuel.com', 'password': 'Admin@123', 'role': 'admin'},
    {'name': 'Engineer User', 'email': 'engineer@efuel.com', 'password': 'Engineer@123', 'role': 'engineer'},
    {'name': 'Viewer User', 'email': 'viewer@efuel.com', 'password': 'Viewer@123', 'role': 'viewer'},
]


async def seed():
    for u in TEST_USERS:
        existing = await users_collection.find_one({'email': u['email']})
        if existing:
            print(f"User already exists: {u['email']}")
            continue
        doc = {
            'id': str(uuid.uuid4()),
            'name': u['name'],
            'email': u['email'],
            'password_hash': hash_password(u['password']),
            'role': u['role'],
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
        }
        await users_collection.insert_one(doc)
        print(f"Created user: {u['email']} / {u['password']} (role={u['role']})")
    await close_db()


if __name__ == '__main__':
    asyncio.run(seed())
