"""
Tests for the embedding utility functions.
"""

import pytest
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from libs.embeddings import embed_text, embed_code, embed_table


def test_embed_text_returns_correct_shape():
    """Test that embed_text returns embeddings with the correct shape."""
    text = "This is a test sentence."
    
    embedding = embed_text(text)
    
    # all-MiniLM-L6-v2 produces 384-dimensional embeddings
    assert embedding.shape == (1, 384)
    
    # Test batch processing
    texts = ["This is the first sentence.", "This is the second one."]
    embeddings = embed_text(texts)
    
    assert embeddings.shape == (2, 384)


def test_embed_code_returns_correct_shape():
    """Test that embed_code returns embeddings with the correct shape."""
    code = """
    def hello_world():
        print("Hello, world!")
    """
    
    embedding = embed_code(code)
    
    # Should have the same dimensions as text embeddings
    assert embedding.shape == (1, 384)
    
    # Test batch processing
    codes = [
        "print('Hello')",
        "def add(a, b):\n    return a + b"
    ]
    embeddings = embed_code(codes)
    
    assert embeddings.shape == (2, 384)


def test_embed_table_returns_correct_shape():
    """Test that embed_table returns embeddings with the correct shape."""
    table = {"name": "John", "age": 30, "city": "New York"}
    
    embedding = embed_table(table)
    
    # Should have the same dimensions as text embeddings
    assert embedding.shape == (1, 384)
    
    # Test batch processing
    tables = [
        {"name": "John", "age": 30, "city": "New York"},
        {"name": "Jane", "age": 25, "city": "San Francisco"}
    ]
    embeddings = embed_table(tables)
    
    assert embeddings.shape == (2, 384)


def test_similar_texts_have_high_similarity():
    """Test that similar texts have a high cosine similarity score."""
    text1 = "The quick brown fox jumps over the lazy dog."
    text2 = "A swift brown fox leaps above the sleepy canine."
    
    embedding1 = embed_text(text1)
    embedding2 = embed_text(text2)
    
    similarity = cosine_similarity(embedding1, embedding2)[0][0]
    
    # Similar sentences should have a relatively high similarity score
    assert similarity > 0.7


def test_identical_text_has_cosine_similarity_gte_08():
    """Test that identical texts have a cosine similarity of at least 0.8."""
    # Test with identical strings
    text = "The quick brown fox jumps over the lazy dog."
    
    embedding1 = embed_text(text)
    embedding2 = embed_text(text)
    
    similarity = cosine_similarity(embedding1, embedding2)[0][0]
    
    # Identical text should have similarity very close to 1.0
    assert similarity >= 0.8
    # It won't be exactly 1.0 due to potential floating-point precision issues
    assert similarity <= 1.0


def test_different_texts_have_lower_similarity():
    """Test that different texts have a lower cosine similarity score."""
    text1 = "The quick brown fox jumps over the lazy dog."
    text2 = "Machine learning models process natural language effectively."
    
    embedding1 = embed_text(text1)
    embedding2 = embed_text(text2)
    
    similarity = cosine_similarity(embedding1, embedding2)[0][0]
    
    # Different topics should have a relatively low similarity score
    assert similarity < 0.7


def test_empty_input_raises_error():
    """Test that empty inputs raise an appropriate error."""
    with pytest.raises(ValueError):
        embed_text("")
    
    with pytest.raises(ValueError):
        embed_code("")
    
    with pytest.raises(ValueError):
        embed_table({})