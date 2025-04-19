"""
API routes for the similarity service.
"""

import logging
import uuid
from typing import Dict, List, Any, Optional, Union
import sys
import os

# Add the parent directory to the path to allow importing the embedding library
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from fastapi import APIRouter, HTTPException, Query, Depends, Response, status
import numpy as np

from app.models import SimilarityRequest, EmbeddingRequest, SimilarityResponse, SimilarityResult
from app.database import search_similar, store_embeddings, is_qdrant_available

# Import the embedding functions from our library
from libs.embeddings import embed_text, embed_code, embed_table

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create the router
router = APIRouter()


@router.post("/similarity", response_model=SimilarityResponse, tags=["similarity"])
async def get_similar_items(
    request: SimilarityRequest,
    response: Response,
):
    """
    Find similar items based on the provided input.
    
    The input can be text, code, or tabular data. Only one of these should be provided.
    
    Args:
        request: SimilarityRequest containing the query and parameters
        
    Returns:
        SimilarityResponse with the search results
    """
    query_type = None
    embedding = None
    
    # Check which type of input was provided and generate the appropriate embedding
    if request.text is not None:
        query_type = "text"
        embedding = embed_text(request.text)
    elif request.code is not None:
        query_type = "code"
        embedding = embed_code(request.code)
    elif request.table is not None:
        query_type = "table"
        embedding = embed_table(request.table)
    else:
        raise HTTPException(
            status_code=400,
            detail="One of 'text', 'code', or 'table' must be provided.",
        )
    
    # Get the first (and only) embedding
    if len(embedding.shape) > 1 and embedding.shape[0] == 1:
        embedding = embedding[0]
    
    # Check if Qdrant is available
    if not is_qdrant_available():
        logger.warning("Qdrant not available, returning empty results")
        response.status_code = status.HTTP_200_OK
        return SimilarityResponse(
            results=[],
            query_type=query_type,
        )
    
    # Search for similar items in the database
    search_results = search_similar(
        embedding=embedding,
        top_k=request.top_k,
        filter_condition=request.filter,
    )
    
    # Convert to response model
    results = [
        SimilarityResult(
            id=result["id"],
            score=result["score"],
            metadata=result["metadata"],
        )
        for result in search_results
    ]
    
    return SimilarityResponse(results=results, query_type=query_type)


@router.post("/store", tags=["storage"])
async def store_items(request: EmbeddingRequest, response: Response):
    """
    Store items in the vector database.
    
    Args:
        request: EmbeddingRequest containing the items to store
        
    Returns:
        Dictionary with the IDs of the stored items
    """
    if not request.items:
        raise HTTPException(
            status_code=400,
            detail="No items provided.",
        )
    
    embeddings = []
    metadata = []
    
    # Process each item and generate the appropriate embedding
    for item in request.items:
        if "text" in item:
            embedding = embed_text(item["text"])
            item_type = "text"
        elif "code" in item:
            embedding = embed_code(item["code"])
            item_type = "code"
        elif "table" in item and isinstance(item["table"], dict):
            embedding = embed_table(item["table"])
            item_type = "table"
        else:
            raise HTTPException(
                status_code=400,
                detail="Each item must contain either 'text', 'code', or 'table'.",
            )
        
        # Get the first (and only) embedding
        if len(embedding.shape) > 1 and embedding.shape[0] == 1:
            embedding = embedding[0]
        
        embeddings.append(embedding)
        
        # Add type to metadata
        item_metadata = item.copy()
        item_metadata["_item_type"] = item_type
        metadata.append(item_metadata)
    
    # Generate IDs if not provided
    ids = request.ids
    if not ids:
        ids = [str(uuid.uuid4()) for _ in range(len(embeddings))]
    elif len(ids) != len(embeddings):
        raise HTTPException(
            status_code=400,
            detail="Number of IDs must match number of items.",
        )
    
    # Check if Qdrant is available
    if not is_qdrant_available():
        logger.warning("Qdrant not available, returning generated IDs without storing embeddings")
        response.status_code = status.HTTP_200_OK
        return {"ids": ids, "storage_status": "skipped"}
    
    # Store the embeddings in the database
    embeddings_array = np.stack(embeddings)
    stored_ids = store_embeddings(
        embeddings=embeddings_array,
        metadata=metadata,
        ids=ids,
    )
    
    return {"ids": stored_ids, "storage_status": "stored"}