from fastapi import FastAPI, HTTPException
from app.db import init_db_pool, pool
from app.ingest_product import router as ingest_product
from app.ingest_service import router as ingest_service
from app.search import router as search
from contextlib import asynccontextmanager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting database initialization...")
    try:
        await init_db_pool()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    yield
    # Shutdown code would go here if needed
    logger.info("Application shutdown")

app = FastAPI(title="Homez AI Search API", lifespan=lifespan)

# Include your routers
app.include_router(ingest_product, prefix="/product")
app.include_router(ingest_service, prefix="/service")
app.include_router(search, prefix="/search")

# Health check endpoint
@app.get("/health")
async def health_check():
    from app.db import pool
    if pool is None:
        raise HTTPException(status_code=503, detail="Database pool not initialized")
    try:
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")
