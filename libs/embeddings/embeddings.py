"""
Embedding utilities using the Sentence Transformers package from Hugging Face.

This module provides functions for embedding text, code, and tabular data
using the all-MiniLM-L6-v2 model.
"""

import logging
import json
from typing import Dict, List, Any, Union, Optional
import numpy as np
from sentence_transformers import SentenceTransformer

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default model
DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"

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
            _model_instance = SentenceTransformer(model_name)
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
    model = get_model()
    
    # Handle single string input
    if isinstance(text, str):
        text = [text]
    
    # Encode the text
    embeddings = model.encode(text, convert_to_numpy=True)
    
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
    model = get_model()
    
    # Handle single string input
    if isinstance(code, str):
        code = [code]
    
    # Preprocess code snippets (remove excessive whitespace, etc.)
    preprocessed_code = []
    for snippet in code:
        # Remove extra blank lines and normalize whitespace
        lines = [line for line in snippet.split('\n') if line.strip()]
        preprocessed = '\n'.join(lines)
        preprocessed_code.append(preprocessed)
    
    # Encode the preprocessed code
    embeddings = model.encode(preprocessed_code, convert_to_numpy=True)
    
    return embeddings


def _table_to_text(table: Dict[str, Any]) -> str:
    """
    Convert a table (dictionary) to a text representation.
    
    Args:
        table: Dictionary representing tabular data
        
    Returns:
        Text representation of the table
    """
    text_parts = []
    
    for key, value in table.items():
        if isinstance(value, (dict, list)):
            # Convert nested structures to JSON strings
            value_str = json.dumps(value, sort_keys=True)
        else:
            value_str = str(value)
        
        text_parts.append(f"{key}: {value_str}")
    
    return "\n".join(text_parts)


def embed_table(table: Union[Dict[str, Any], List[Dict[str, Any]]]) -> np.ndarray:
    """
    Embed tabular data by converting it to a text representation first.
    
    Args:
        table: Dictionary or list of dictionaries representing tabular data
        
    Returns:
        Numpy array of embeddings with shape (n_samples, embedding_dim)
    """
    # Handle single dictionary input
    if isinstance(table, dict):
        table = [table]
    
    # Convert tables to text
    table_texts = [_table_to_text(t) for t in table]
    
    # Embed the text representations
    return embed_text(table_texts)