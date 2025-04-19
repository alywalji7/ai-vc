"""
Database client for connecting to Qdrant vector database.
"""

import logging
import uuid
from typing import Dict, List, Any, Optional, Union

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import ResponseHandlingException, UnexpectedResponse
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
# Flag to indicate if Qdrant is available
_qdrant_available = False


def get_client() -> Optional[QdrantClient]:
    """
    Get the Qdrant client, using a singleton pattern.
    
    Returns:
        QdrantClient instance or None if connection fails
    """
    global _client_instance, _qdrant_available
    
    if _client_instance is None and not _qdrant_available:
        logger.info(f"Connecting to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}...")
        try:
            _client_instance = QdrantClient(
                host=QDRANT_HOST,
                port=QDRANT_PORT,
                grpc_port=QDRANT_GRPC_PORT,
                api_key=QDRANT_API_KEY,
                timeout=5.0,
            )
            # Test connection
            _client_instance.get_collections()
            _qdrant_available = True
            logger.info("Connected to Qdrant successfully")
        except Exception as e:
            logger.error(f"Error connecting to Qdrant: {str(e)}")
            _client_instance = None
            _qdrant_available = False
    
    return _client_instance


def is_qdrant_available() -> bool:
    """Check if Qdrant is available."""
    return get_client() is not None and _qdrant_available


def ensure_collection_exists() -> bool:
    """
    Ensure that the vector collection exists, creating it if necessary.
    
    Returns:
        True if collection exists or was created, False otherwise
    """
    client = get_client()
    if not client:
        return False
    
    try:
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
        return True
    except (ResponseHandlingException, UnexpectedResponse) as e:
        logger.error(f"Error ensuring collection exists: {str(e)}")
        return False


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
    
    # Generate IDs if not provided
    if not ids:
        ids = [str(uuid.uuid4()) for _ in range(len(embeddings))]
    elif len(ids) != len(embeddings):
        raise ValueError("Number of IDs must match number of embeddings")
    
    client = get_client()
    if not client or not ensure_collection_exists():
        logger.warning("Qdrant not available, returning generated IDs without storing embeddings")
        return ids
    
    try:
        # Prepare points for insertion
        points = []
        for i, embedding in enumerate(embeddings):
            point = models.PointStruct(
                id=ids[i],
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
    except Exception as e:
        logger.error(f"Error storing embeddings: {str(e)}")
        # Return the generated IDs even if storage fails
        return ids


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
    if not client or not ensure_collection_exists():
        logger.warning("Qdrant not available, returning empty results")
        return []
    
    try:
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
    except Exception as e:
        logger.error(f"Error searching for similar embeddings: {str(e)}")
        return []