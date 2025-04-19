"""
Script to test the similarity search functionality.
"""

import sys
import os
import json
import logging
import requests
from pprint import pprint

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API endpoint URLs
BASE_URL = "http://localhost:8090"
SIMILARITY_URL = f"{BASE_URL}/api/v1/similarity"
STORE_URL = f"{BASE_URL}/api/v1/store"


def test_store_items():
    """Test storing items in the vector database."""
    # Sample items to store
    items = [
        {
            "text": "How to implement a binary search tree in Python",
            "source": "stackoverflow",
            "created_at": "2025-04-19T10:00:00Z"
        },
        {
            "code": """
def binary_search(arr, x):
    low = 0
    high = len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] < x:
            low = mid + 1
        elif arr[mid] > x:
            high = mid - 1
        else:
            return mid
    return -1
            """,
            "language": "python",
            "source": "github",
            "created_at": "2025-04-19T11:00:00Z"
        },
        {
            "table": {
                "name": "Binary Search Algorithm",
                "time_complexity": "O(log n)",
                "space_complexity": "O(1)",
                "usage": "Searching in sorted arrays"
            },
            "source": "wikipedia",
            "created_at": "2025-04-19T12:00:00Z"
        }
    ]
    
    # Make the request to store items
    response = requests.post(STORE_URL, json={"items": items})
    
    # Check the response
    logger.info(f"Store response status: {response.status_code}")
    if response.status_code == 200:
        logger.info("Items stored successfully!")
        logger.info(f"Stored item IDs: {response.json()['ids']}")
        return response.json()['ids']
    else:
        logger.error(f"Error storing items: {response.text}")
        return None


def test_similarity_search(item_type="text", query=None, top_k=5):
    """Test similarity search functionality."""
    if query is None:
        if item_type == "text":
            query = "Python implementation of binary search"
        elif item_type == "code":
            query = """
def binary_search(array, target):
    start = 0
    end = len(array) - 1
    while start <= end:
        middle = (start + end) // 2
        if array[middle] < target:
            start = middle + 1
        elif array[middle] > target:
            end = middle - 1
        else:
            return middle
    return -1
            """
        elif item_type == "table":
            query = {
                "name": "Binary Search",
                "time_complexity": "O(log n)",
                "space_complexity": "O(1)"
            }
    
    # Prepare the request payload
    payload = {
        "top_k": top_k
    }
    payload[item_type] = query
    
    # Make the request
    response = requests.post(SIMILARITY_URL, json=payload)
    
    # Check the response
    logger.info(f"Search response status: {response.status_code}")
    if response.status_code == 200:
        logger.info("Search successful!")
        results = response.json()
        logger.info(f"Query type: {results['query_type']}")
        logger.info(f"Number of results: {len(results['results'])}")
        
        # Print each result with its similarity score
        for i, result in enumerate(results['results']):
            logger.info(f"Result {i+1}, Score: {result['score']:.4f}")
            pprint(result['metadata'])
            logger.info("-----")
        
        return results
    else:
        logger.error(f"Error searching: {response.text}")
        return None


if __name__ == "__main__":
    logger.info("Testing embeddings functionality...")
    
    # Store some items first
    stored_ids = test_store_items()
    
    if stored_ids:
        # Test text similarity search
        logger.info("\n\nTesting text similarity search...")
        test_similarity_search(item_type="text")
        
        # Test code similarity search
        logger.info("\n\nTesting code similarity search...")
        test_similarity_search(item_type="code")
        
        # Test table similarity search
        logger.info("\n\nTesting table similarity search...")
        test_similarity_search(item_type="table")
    
    logger.info("Testing completed!")