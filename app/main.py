from fastapi import FastAPI, HTTPException
from app.db import init_db_pool, pool
from app.ingest_product import router as ingest_product
from app.ingest_service import router as ingest_service
from app.search import router as search
from contextlib import asynccontextmanager
import logging
import asyncio
import sys
import os

# Add the root directory to the Python path so we can import rabbitmq_consumer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables to hold the consumer tasks and event
consumer_tasks = None
consumer_shutdown_event = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global consumer_tasks, consumer_shutdown_event
    
    logger.info("Starting database initialization...")
    try:
        await init_db_pool()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    # Start RabbitMQ consumer
    try:
        logger.info("Starting RabbitMQ consumer...")
        # Import the consumer functions
        import rabbitmq_consumer
        
        # Create shutdown event for consumers
        consumer_shutdown_event = asyncio.Event()
        rabbitmq_consumer.shutdown_event = consumer_shutdown_event
        
        # Create tasks for both consumers
        consumer_tasks = [
            asyncio.create_task(rabbitmq_consumer.consume_products()),
            asyncio.create_task(rabbitmq_consumer.consume_services())
        ]
        logger.info("RabbitMQ consumers started successfully")
    except Exception as e:
        logger.error(f"Failed to start RabbitMQ consumer: {e}")
        # Don't raise here as we want the API to continue running even if consumer fails

    yield
    
    # Shutdown code
    logger.info("Shutting down application...")
    # Signal consumers to stop if they exist
    if consumer_shutdown_event:
        logger.info("Stopping RabbitMQ consumers...")
        consumer_shutdown_event.set()
        
    # Wait for consumer tasks to complete
    if consumer_tasks:
        try:
            await asyncio.gather(*consumer_tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error stopping consumers: {e}")
    logger.info("Application shutdown complete")

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