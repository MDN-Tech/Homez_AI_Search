from sentence_transformers import SentenceTransformer
import asyncio

# Initialize the sentence transformer model
# Using a model that produces 768-dimensional embeddings to match the database schema
model = SentenceTransformer('all-mpnet-base-v2')

async def embed_text(text: str):
    # Run the embedding in a separate thread to avoid blocking
    embedding = await asyncio.get_event_loop().run_in_executor(None, model.encode, text)
    # Convert numpy array to list for database storage
    return embedding.tolist()

async def embed_texts(texts: list):
    # Run multiple embeddings in a separate thread to avoid blocking
    embeddings = await asyncio.get_event_loop().run_in_executor(None, model.encode, texts)
    # Convert numpy array to list for database storage
    return [embedding.tolist() for embedding in embeddings]