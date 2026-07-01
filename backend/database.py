"""
MongoDB (Motor async) connection + index setup for EFUEL Engineering Hub.
"""
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

logger = logging.getLogger(__name__)

client = AsyncIOMotorClient(settings.MONGO_URL)
db = client[settings.DB_NAME]

# Collections
users_collection = db['users']
products_collection = db['products']
brands_collection = db['brands']
categories_collection = db['categories']
specifications_collection = db['specifications']
documents_collection = db['documents']
search_history_collection = db['search_history']
compare_history_collection = db['compare_history']
favorites_collection = db['favorites']
bom_projects_collection = db['bom_projects']
ai_cache_collection = db['ai_cache']
api_logs_collection = db['api_logs']
system_settings_collection = db['system_settings']
chat_sessions_collection = db['chat_sessions']


async def init_indexes():
    """Create indexes required for performance & uniqueness. Safe to call repeatedly."""
    try:
        await ai_cache_collection.create_index('query_hash', unique=True)
        await ai_cache_collection.create_index('created_at')
        await ai_cache_collection.create_index('category')

        await users_collection.create_index('email', unique=True)

        await search_history_collection.create_index([('user_id', 1), ('created_at', -1)])
        await compare_history_collection.create_index([('user_id', 1), ('created_at', -1)])
        await favorites_collection.create_index([('user_id', 1), ('product_id', 1)], unique=True)

        await api_logs_collection.create_index('created_at')
        await api_logs_collection.create_index('stage')

        await products_collection.create_index('name')
        await products_collection.create_index('category')
        await products_collection.create_index('brand')

        await documents_collection.create_index('product_id')
        await bom_projects_collection.create_index([('user_id', 1), ('created_at', -1)])
        logger.info('MongoDB indexes ensured successfully')
    except Exception as e:
        logger.error(f'Error creating indexes: {e}')


async def close_db():
    client.close()
