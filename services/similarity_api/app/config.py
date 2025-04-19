"""
Configuration for the similarity API service.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Qdrant configuration
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_GRPC_PORT = int(os.getenv("QDRANT_GRPC_PORT", "6334"))
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "embeddings")
QDRANT_VECTOR_SIZE = 384  # all-MiniLM-L6-v2 produces 384-dimensional embeddings

# API configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8090"))
API_DEBUG = os.getenv("API_DEBUG", "False").lower() in ("true", "1", "t")

# Model configuration
MODEL_NAME = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")
MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR", "./model_cache")