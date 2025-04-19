"""
Database client for connecting to Qdrant vector database.
"""

import logging
from typing import Dict, List, Any, Optional, Union

from qdrant_client import QdrantClient
from qdrant_client.http import models
import numpy as np

from app.config import (
    QDRANT_HOST,
    QDRANT_PORT,
    QDRANT_GRPC_PORT,
    QDRANT_API_KEY,
    QDRANT_COLLECTION_NAME,
    QDRANT_VECTOR_SIZE,
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Singleton client instance
_client_instance = None


def get_client() -> QdrantClient:
    """
    Get the Qdrant client, using a singleton pattern.
    
    Returns:
        QdrantClient instance
    """
    global _client_instance
    
    if _client_instance is None:
        logger.info(f"Connecting to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}...")
        try:
            _client_instance = QdrantClient(
                host=QDRANT_HOST,
                port=QDRANT_PORT,
                grpc_port=QDRANT_GRPC_PORT,
                api_key=QDRANT_API_KEY,
                timeout=10.0,
            )
            logger.info("Connected to Qdrant successfully")
        except Exception as e:
            logger.error(f"Error connecting to Qdrant: {str(e)}")
            raise
    
    return _client_instance


def ensure_collection_exists() -> None:
    """
    Ensure that the vector collection exists, creating it if necessary.
    """
    client = get_client()
    
    # Check if collection exists
    collections = client.get_collections().collections
    collection_names = [collection.name for collection in collections]
    
    if QDRANT_COLLECTION_NAME not in collection_names:
        logger.info(f"Creating collection '{QDRANT_COLLECTION_NAME}'...")
        client.create_collection(
            collection_name=QDRANT_COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=QDRANT_VECTOR_SIZE,
                distance=models.Distance.COSINE,
            ),
        )
        logger.info(f"Collection '{QDRANT_COLLECTION_NAME}' created successfully")
    else:
        logger.info(f"Collection '{QDRANT_COLLECTION_NAME}' already exists")


def store_embeddings(
    embeddings: np.ndarray,
    metadata: List[Dict[str, Any]],
    ids: Optional[List[str]] = None,
) -> List[str]:
    """
    Store embeddings in the vector database.
    
    Args:
        embeddings: Numpy array of embeddings with shape (n_samples, embedding_dim)
        metadata: List of metadata dictionaries for each embedding
        ids: Optional list of IDs for the points. If not provided, random UUIDs will be generated.
        
    Returns:
        List of IDs for the stored points
    """
    if len(embeddings) != len(metadata):
        raise ValueError("Number of embeddings must match number of metadata entries")
    
    client = get_client()
    ensure_collection_exists()
    
    # Prepare points for insertion
    points = []
    for i, embedding in enumerate(embeddings):
        point = models.PointStruct(
            id=ids[i] if ids else None,
            vector=embedding.tolist(),
            payload=metadata[i],
        )
        points.append(point)
    
    # Insert points into the collection
    result = client.upsert(
        collection_name=QDRANT_COLLECTION_NAME,
        points=points,
    )
    
    return result.result


def search_similar(
    embedding: np.ndarray,
    top_k: int = 5,
    filter_condition: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Search for similar vectors in the database.
    
    Args:
        embedding: Query embedding vector
        top_k: Number of most similar results to return
        filter_condition: Optional filter condition for the search
        
    Returns:
        List of dictionaries with search results, each containing 'id', 'score', and 'metadata'
    """
    client = get_client()
    ensure_collection_exists()
    
    # Prepare filter if any
    filter_query = None
    if filter_condition:
        filter_query = models.Filter(**filter_condition)
    
    # Search for similar vectors
    search_results = client.search(
        collection_name=QDRANT_COLLECTION_NAME,
        query_vector=embedding.tolist(),
        limit=top_k,
        query_filter=filter_query,
    )
    
    # Format the results
    results = []
    for result in search_results:
        results.append({
            "id": result.id,
            "score": result.score,
            "metadata": result.payload,
        })
    
    return results