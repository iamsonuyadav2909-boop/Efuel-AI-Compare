from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
import logging

from config import settings
from database import init_indexes, close_db
from routes.auth_routes import router as auth_router
from routes.research_routes import router as research_router
from routes.compare_routes import router as compare_router
from routes.chat_routes import router as chat_router
from routes.bom_routes import router as bom_router
from routes.misc_routes import router as misc_router
from routes.admin_routes import router as admin_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create the main app without a prefix
app = FastAPI(title='EFUEL Engineering Hub API', version='1.0.0')

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


@api_router.get("/")
async def root():
    return {"message": "EFUEL Engineering Hub API", "status": "operational"}


@api_router.get("/health")
async def health():
    return {
        "status": "healthy",
        "tavily_configured": settings.tavily_enabled,
        "firecrawl_configured": settings.firecrawl_enabled,
        "llm_configured": settings.llm_enabled,
    }


api_router.include_router(auth_router)
api_router.include_router(research_router)
api_router.include_router(compare_router)
api_router.include_router(chat_router)
api_router.include_router(bom_router)
api_router.include_router(misc_router)
api_router.include_router(admin_router)

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=settings.CORS_ORIGINS.split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await init_indexes()
    logger.info('EFUEL Engineering Hub API started successfully')


@app.on_event("shutdown")
async def shutdown_db_client():
    await close_db()
