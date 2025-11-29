from fastapi import APIRouter, Query
from app.embedding_utils import embed_text
from pydantic import BaseModel
from typing import List
from app.models import Product, Service
import json
import logging

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SearchResponse(BaseModel):
    products: List[Product] = []
    services: List[Service] = []


router = APIRouter()

@router.get("/", response_model=SearchResponse)
async def search(query: str = Query(..., description="Search query"),
                 limit: int = Query(2, description="Number of results per type")):
    """
    Search both products and services using semantic embeddings + cosine similarity
    Returns top `limit` products and top `limit` services
    """

    # 1️⃣ Generate a single embedding for the query
    query_embedding = await embed_text(query)
    
    # Import pool inside the function to ensure it's initialized
    from app.db import pool

    async with pool.acquire() as conn:

        # 2️⃣ Search products (single cosine similarity using pgvector)
        products_rows = await conn.fetch("""
            SELECT p.*, 1 - (pe.embedding <=> $1) AS score
            FROM product_embeddings pe
            JOIN products p ON pe.product_id = p.id
            ORDER BY embedding <=> $1
            LIMIT $2
        """, query_embedding, limit)

        # 3️⃣ Search services (single cosine similarity using pgvector)
        services_rows = await conn.fetch("""
            SELECT s.*, 1 - (se.embedding <=> $1) AS score
            FROM service_embeddings se
            JOIN services s ON se.service_id = s.id
            ORDER BY embedding <=> $1
            LIMIT $2
        """, query_embedding, limit)

    # 4️⃣ Convert DB rows to Pydantic models
    # Parse JSON fields properly
    products = []
    for row in products_rows:
        row_dict = dict(row)
        # Log the score
        score = row_dict.get('score', 0)
        logger.info(f"Product '{row_dict.get('name', 'Unknown')}' score: {score}")
        # Remove the score field as it's not part of the Product model
        row_dict.pop('score', None)
        # Parse JSON fields
        if 'tags' in row_dict and isinstance(row_dict['tags'], str):
            row_dict['tags'] = json.loads(row_dict['tags'])
        if 'variants' in row_dict and isinstance(row_dict['variants'], str):
            row_dict['variants'] = json.loads(row_dict['variants'])
        if 'metadata' in row_dict and isinstance(row_dict['metadata'], str):
            row_dict['metadata'] = json.loads(row_dict['metadata'])
        # Ensure required fields are present
        if 'categoryName' not in row_dict or row_dict['categoryName'] is None:
            row_dict['categoryName'] = 'Unknown'
        try:
            products.append(Product.parse_obj(row_dict))
        except Exception as e:
            print(f"Error parsing product: {e}, row_dict: {row_dict}")
            # Continue with other products even if one fails
            pass
    
    services = []
    for row in services_rows:
        row_dict = dict(row)
        # Log the score
        score = row_dict.get('score', 0)
        logger.info(f"Service '{row_dict.get('name', 'Unknown')}' score: {score}")
        # Remove the score field as it's not part of the Service model
        row_dict.pop('score', None)
        # Parse JSON fields
        if 'tags' in row_dict and isinstance(row_dict['tags'], str):
            row_dict['tags'] = json.loads(row_dict['tags'])
        if 'packages' in row_dict and isinstance(row_dict['packages'], str):
            row_dict['packages'] = json.loads(row_dict['packages'])
        if 'metadata' in row_dict and isinstance(row_dict['metadata'], str):
            row_dict['metadata'] = json.loads(row_dict['metadata'])
        # Ensure required fields are present
        if 'categoryName' not in row_dict or row_dict['categoryName'] is None:
            row_dict['categoryName'] = 'Unknown'
        try:
            services.append(Service.parse_obj(row_dict))
        except Exception as e:
            print(f"Error parsing service: {e}, row_dict: {row_dict}")
            # Continue with other services even if one fails
            pass

    # 5️⃣ Return typed response
    return SearchResponse(products=products, services=services)