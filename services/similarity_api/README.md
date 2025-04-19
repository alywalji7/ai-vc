# Similarity API Service

This service provides vector similarity search functionality using the Sentence Transformers package from Hugging Face and Qdrant vector database.

## Features

- Text, code, and tabular data embedding
- Vector similarity search
- Filtering by metadata
- API and CLI interfaces

## API Endpoints

### GET /

Root endpoint returning service information.

### GET /health

Health check endpoint.

### POST /api/v1/similarity

Find similar items based on a text, code, or tabular data query.

Request body:
```json
{
  "text": "How to implement a binary search tree in Python", 
  "top_k": 5
}
```

Or:
```json
{
  "code": "def binary_search(arr, x):\n    low = 0\n    high = len(arr) - 1\n    mid = 0\n    while low <= high:\n        mid = (high + low) // 2\n        if arr[mid] < x:\n            low = mid + 1\n        elif arr[mid] > x:\n            high = mid - 1\n        else:\n            return mid\n    return -1",
  "top_k": 5
}
```

Or:
```json
{
  "table": {
    "name": "Binary Search Algorithm",
    "time_complexity": "O(log n)",
    "space_complexity": "O(1)"
  },
  "top_k": 5
}
```

Response:
```json
{
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
```

### POST /api/v1/store

Store items in the vector database.

Request body:
```json
{
  "items": [
    {
      "text": "How to implement a binary search tree in Python",
      "source": "stackoverflow",
      "created_at": "2025-04-19T10:00:00Z"
    },
    {
      "code": "def binary_search(arr, x):\n    low = 0\n    high = len(arr) - 1\n    mid = 0\n    while low <= high:\n        mid = (high + low) // 2\n        if arr[mid] < x:\n            low = mid + 1\n        elif arr[mid] > x:\n            high = mid - 1\n        else:\n            return mid\n    return -1",
      "language": "python",
      "source": "github",
      "created_at": "2025-04-19T11:00:00Z"
    }
  ]
}
```

Response:
```json
{
  "ids": ["1", "2"]
}
```

## CLI Usage

### Store Items

```bash
python cli.py store --text "How to implement a binary search tree in Python"
python cli.py store --code "def binary_search(arr, x): ..." --language python
python cli.py store --file items.json
```

### Search for Similar Items

```bash
python cli.py search --text "Python implementation of binary search"
python cli.py search --code "def binary_search(array, target): ..." --top-k 10
python cli.py search --table --table-file table_data.json --output results.json
```

### Generate Embeddings

```bash
python cli.py embed --text "How to implement a binary search tree in Python" --output embedding.json
python cli.py embed --code "def binary_search(arr, x): ..."
python cli.py embed --table --table-file table_data.json
```

## Configuration

Configuration is stored in `app/config.py` and can be overridden using environment variables:

- `QDRANT_HOST`: Host of the Qdrant vector database (default: localhost)
- `QDRANT_PORT`: HTTP port of the Qdrant vector database (default: 6333)
- `QDRANT_GRPC_PORT`: gRPC port of the Qdrant vector database (default: 6334)
- `QDRANT_API_KEY`: API key for the Qdrant vector database (default: None)
- `QDRANT_COLLECTION_NAME`: Name of the vector collection (default: embeddings)
- `API_HOST`: Host to bind the API server to (default: 0.0.0.0)
- `API_PORT`: Port to bind the API server to (default: 8090)
- `API_DEBUG`: Enable debug mode (default: False)
- `MODEL_NAME`: Name of the Sentence Transformer model (default: all-MiniLM-L6-v2)
- `MODEL_CACHE_DIR`: Directory to cache the model files (default: ./model_cache)

## Embedding Model

This service uses the [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) model from Hugging Face Sentence Transformers for generating embeddings. This model produces 384-dimensional embeddings and has good performance for semantic similarity search across various domains.

## Development

### Prerequisites

- Python 3.11+
- Qdrant vector database (can be run using Docker)
- Sentence Transformers and related dependencies

### Installation

```bash
pip install -r requirements.txt
```

### Running the Service

```bash
python main.py
```

### Testing

To test the functionality:

```bash
python test_embeddings.py
```