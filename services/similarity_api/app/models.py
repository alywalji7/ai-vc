"""
Pydantic models for request and response data validation.
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field


class SimilarityRequest(BaseModel):
    """Model for similarity search request."""
    text: Optional[str] = Field(None, description="Text to search for similar items")
    code: Optional[str] = Field(None, description="Code snippet to search for similar items")
    table: Optional[Dict[str, Any]] = Field(None, description="Table data to search for similar items")
    filter: Optional[Dict[str, Any]] = Field(None, description="Optional filter criteria for the search")
    top_k: int = Field(5, description="Number of results to return", ge=1, le=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "How to implement a binary search tree in Python",
                "top_k": 5
            }
        }


class EmbeddingRequest(BaseModel):
    """Model for storing embeddings request."""
    items: List[Dict[str, Any]] = Field(..., description="List of items to embed and store")
    ids: Optional[List[str]] = Field(None, description="Optional list of IDs for the items")
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {"text": "How to implement a binary search tree in Python"},
                    {"code": "def binary_search(arr, x):\n    low = 0\n    high = len(arr) - 1\n    mid = 0\n    while low <= high:\n        mid = (high + low) // 2\n        if arr[mid] < x:\n            low = mid + 1\n        elif arr[mid] > x:\n            high = mid - 1\n        else:\n            return mid\n    return -1"}
                ]
            }
        }


class SimilarityResult(BaseModel):
    """Model for a single similarity search result."""
    id: Union[str, int] = Field(..., description="ID of the item")
    score: float = Field(..., description="Similarity score")
    metadata: Dict[str, Any] = Field(..., description="Metadata associated with the item")


class SimilarityResponse(BaseModel):
    """Model for similarity search response."""
    results: List[SimilarityResult] = Field(..., description="List of similarity search results")
    query_type: str = Field(..., description="Type of query performed (text, code, or table)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "id": "1",
                        "score": 0.92,
                        "metadata": {
                            "text": "Python implementation of a binary search tree",
                            "created_at": "2025-04-15T14:22:10Z"
                        }
                    }
                ],
                "query_type": "text"
            }
        }