"""
Tests for embedding utilities.
"""

import pytest
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from libs.embeddings import embed_text, embed_code, embed_table


def test_embed_text_shape():
    """Test that the embed_text function returns embeddings with the expected shape."""
    text = "This is a test"
    embedding = embed_text(text)
    
    # The embedding should be a 1D array with 384 dimensions (for all-MiniLM-L6-v2)
    assert embedding.shape == (1, 384)
    
    # Test with a list of strings
    texts = ["This is a test", "This is another test"]
    embeddings = embed_text(texts)
    
    # The embeddings should be a 2D array with shape (2, 384)
    assert embeddings.shape == (2, 384)


def test_embed_code_shape():
    """Test that the embed_code function returns embeddings with the expected shape."""
    code = """
    def test_function():
        return "Hello, world!"
    """
    embedding = embed_code(code)
    
    # The embedding should be a 1D array with 384 dimensions
    assert embedding.shape == (1, 384)
    
    # Test with a list of code snippets
    codes = [
        """
        def test_function():
            return "Hello, world!"
        """,
        """
        class TestClass:
            def __init__(self):
                self.message = "Hello, world!"
        """
    ]
    embeddings = embed_code(codes)
    
    # The embeddings should be a 2D array with shape (2, 384)
    assert embeddings.shape == (2, 384)


def test_embed_table_shape():
    """Test that the embed_table function returns embeddings with the expected shape."""
    table = {
        "name": "John Doe",
        "age": 30,
        "email": "john.doe@example.com"
    }
    embedding = embed_table(table)
    
    # The embedding should be a 1D array with 384 dimensions
    assert embedding.shape == (1, 384)
    
    # Test with a list of tables
    tables = [
        {
            "name": "John Doe",
            "age": 30,
            "email": "john.doe@example.com"
        },
        {
            "name": "Jane Smith",
            "age": 25,
            "email": "jane.smith@example.com"
        }
    ]
    embeddings = embed_table(tables)
    
    # The embeddings should be a 2D array with shape (2, 384)
    assert embeddings.shape == (2, 384)


def test_text_similarity():
    """Test that similar texts have high cosine similarity."""
    text1 = "How to implement a binary search tree in Python"
    text2 = "Python implementation of a binary search tree"
    
    embedding1 = embed_text(text1)
    embedding2 = embed_text(text2)
    
    # Calculate cosine similarity
    similarity = cosine_similarity(embedding1, embedding2)[0][0]
    
    # The similarity should be high (> 0.8) for very similar texts
    assert similarity > 0.8, f"Similarity {similarity} is not > 0.8"


def test_code_similarity():
    """Test that similar code snippets have high cosine similarity."""
    code1 = """
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
    """
    
    code2 = """
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
    
    embedding1 = embed_code(code1)
    embedding2 = embed_code(code2)
    
    # Calculate cosine similarity
    similarity = cosine_similarity(embedding1, embedding2)[0][0]
    
    # The similarity should be high (> 0.8) for very similar code snippets
    assert similarity > 0.8, f"Similarity {similarity} is not > 0.8"


def test_table_similarity():
    """Test that similar tables have high cosine similarity."""
    table1 = {
        "name": "John Doe",
        "age": 30,
        "email": "john.doe@example.com"
    }
    
    table2 = {
        "name": "John Doe",
        "age": 30,
        "email": "john.doe@example.org"
    }
    
    embedding1 = embed_table(table1)
    embedding2 = embed_table(table2)
    
    # Calculate cosine similarity
    similarity = cosine_similarity(embedding1, embedding2)[0][0]
    
    # The similarity should be high (> 0.8) for very similar tables
    assert similarity > 0.8, f"Similarity {similarity} is not > 0.8"