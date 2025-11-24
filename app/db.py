import asyncpg
import os
from dotenv import load_dotenv
from typing import Optional
import logging

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Validate that DATABASE_URL is set
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set. Please create a .env file with DATABASE_URL.")

# Set up logger
logger = logging.getLogger("db")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

# Global pool
pool: Optional[asyncpg.pool.Pool] = None

async def init_db_pool():
    """
    Initialize asyncpg connection pool and log status
    """
    global pool
    
    # Check if DATABASE_URL is set
    if not DATABASE_URL:
        logger.error("DATABASE_URL environment variable is not set")
        raise ValueError("DATABASE_URL environment variable is not set. Please create a .env file with DATABASE_URL.")
    
    logger.info(f"Attempting to connect to database with URL: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
    logger.info(f"Full DATABASE_URL: {DATABASE_URL}")
    
    if pool is None:
        try:
            logger.info("Creating database pool...")
            pool = await asyncpg.create_pool(
                dsn=DATABASE_URL,
                min_size=1,
                max_size=10
            )
            logger.info("✅ Database pool initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize database pool: {type(e).__name__}: {e}")
            logger.error(f"Database URL: {DATABASE_URL}")
            logger.error("Troubleshooting steps:")
            logger.error("1. Make sure PostgreSQL is running")
            logger.error("2. Verify the database 'Homez_AI_Search' exists")
            logger.error("3. Check that the username/password are correct")
            logger.error("4. Ensure pgvector extension is installed in PostgreSQL")
            # Let's also try a simple connection to get more details
            try:
                conn = await asyncpg.connect(DATABASE_URL)
                await conn.close()
                logger.info("Direct connection successful, but pool creation failed")
            except Exception as direct_e:
                logger.error(f"Direct connection also failed: {type(direct_e).__name__}: {direct_e}")
            raise

# Optional: wrapper to log whenever a connection is acquired
async def acquire_connection():
    if pool is None:
        raise RuntimeError("Database pool is not initialized. Call init_db_pool() first.")
    async with pool.acquire() as conn:
        logger.info("🔗 Acquired a database connection")
        yield conn
