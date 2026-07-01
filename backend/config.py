"""
Centralized configuration for EFUEL Engineering Hub backend.
All secrets/config are read from environment variables (.env) - never hardcoded.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')


class Settings:
    # Mongo
    MONGO_URL: str = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    DB_NAME: str = os.environ.get('DB_NAME', 'efuel_db')
    CORS_ORIGINS: str = os.environ.get('CORS_ORIGINS', '*')

    # LLM (Emergent Universal Key)
    EMERGENT_LLM_KEY: str = os.environ.get('EMERGENT_LLM_KEY', '')
    LLM_PROVIDER: str = os.environ.get('LLM_PROVIDER', 'openai')
    LLM_MODEL: str = os.environ.get('LLM_MODEL', 'gpt-4o')

    # Tavily (fallback search provider)
    TAVILY_API_KEY: str = os.environ.get('TAVILY_API_KEY', '')

    # Exa (PRIMARY search provider - semantic search). Optional until user configures.
    EXA_API_KEY: str = os.environ.get('EXA_API_KEY', '')

    # Firecrawl (placeholder until user provides)
    FIRECRAWL_API_KEY: str = os.environ.get('FIRECRAWL_API_KEY', '')

    # Encryption key for Admin-configured API credentials stored in MongoDB
    CREDENTIAL_ENCRYPTION_KEY: str = os.environ.get('CREDENTIAL_ENCRYPTION_KEY', '')

    # Auth
    JWT_SECRET: str = os.environ.get('JWT_SECRET', 'change-me')
    JWT_ALGORITHM: str = os.environ.get('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRE_MINUTES: int = int(os.environ.get('JWT_EXPIRE_MINUTES', '10080'))

    @property
    def tavily_enabled(self) -> bool:
        return bool(self.TAVILY_API_KEY and self.TAVILY_API_KEY.strip())

    @property
    def exa_enabled(self) -> bool:
        return bool(self.EXA_API_KEY and self.EXA_API_KEY.strip())

    @property
    def firecrawl_enabled(self) -> bool:
        return bool(self.FIRECRAWL_API_KEY and self.FIRECRAWL_API_KEY.strip())

    @property
    def llm_enabled(self) -> bool:
        return bool(self.EMERGENT_LLM_KEY and self.EMERGENT_LLM_KEY.strip())


settings = Settings()
