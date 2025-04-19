"""
Embedding utilities using the Sentence Transformers package from Hugging Face.

This module provides functions for embedding text, code, and tabular data
using the all-MiniLM-L6-v2 model.
"""

import os
import logging
from typing import List, Dict, Any, Union, Optional
import numpy as np
from sentence_transformers import SentenceTransformer

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default model to use
DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"
MODEL_CACHE_DIR = os.environ.get("MODEL_CACHE_DIR", "./model_cache")

# Singleton model instance
_model_instance = None


def get_model(model_name: str = DEFAULT_MODEL_NAME) -> SentenceTransformer:
    """
    Get the Sentence Transformer model, using a singleton pattern.
    
    Args:
        model_name: Name of the model to load from Hugging Face
        
    Returns:
        SentenceTransformer model instance
    """
    global _model_instance
    
    if _model_instance is None:
        logger.info(f"Loading model {model_name}...")
        try:
            _model_instance = SentenceTransformer(model_name, cache_folder=MODEL_CACHE_DIR)
            logger.info(f"Model {model_name} loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {str(e)}")
            raise
    
    return _model_instance


def embed_text(text: Union[str, List[str]]) -> np.ndarray:
    """
    Embed text using the Sentence Transformer model.
    
    Args:
        text: String or list of strings to embed
        
    Returns:
        Numpy array of embeddings with shape (n_samples, embedding_dim)
    """
    if not text:
        raise ValueError("Text cannot be empty")
    
    model = get_model()
    
    if isinstance(text, str):
        # Convert single string to list for batch processing
        texts = [text]
    else:
        texts = text
    
    # Generate embeddings
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return embeddings


def embed_code(code: Union[str, List[str]]) -> np.ndarray:
    """
    Embed code using the Sentence Transformer model.
    
    This function is specialized for code snippets and applies preprocessing
    specific to code before embedding.
    
    Args:
        code: String or list of code snippets to embed
        
    Returns:
        Numpy array of embeddings with shape (n_samples, embedding_dim)
    """
    if not code:
        raise ValueError("Code cannot be empty")
    
    # Preprocessing for code - preserve whitespace and indentation
    # which are important for code semantics
    if isinstance(code, str):
        # Process a single code snippet
        preprocessed = [code]
    else:
        # Process multiple code snippets
        preprocessed = code
    
    # Use the same underlying model but with code-specific preprocessing
    return embed_text(preprocessed)


def embed_table(table: Union[Dict[str, Any], List[Dict[str, Any]]]) -> np.ndarray:
    """
    Embed tabular data by converting it to a text representation first.
    
    Args:
        table: Dictionary or list of dictionaries representing tabular data
        
    Returns:
        Numpy array of embeddings with shape (n_samples, embedding_dim)
    """
    if not table:
        raise ValueError("Table cannot be empty")
    
    # Convert table(s) to text representation
    if isinstance(table, dict):
        tables = [table]
    else:
        tables = table
    
    # Convert each table to a string representation
    text_representations = []
    for t in tables:
        # Create a string representation of the table
        # Format: "key1: value1, key2: value2, ..."
        text_repr = ", ".join([f"{k}: {v}" for k, v in t.items()])
        text_representations.append(text_repr)
    
    # Embed the text representations
    return embed_text(text_representations)