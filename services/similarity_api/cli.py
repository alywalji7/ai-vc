"""
Command-line interface for the similarity API service.
"""

import sys
import os
import argparse
import logging
import json
import requests
from pprint import pprint

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to the path to allow importing the embedding library
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from libs.embeddings import embed_text, embed_code, embed_table

# API endpoint URLs
DEFAULT_BASE_URL = "http://localhost:8090"
SIMILARITY_URL = lambda base_url: f"{base_url}/api/v1/similarity"
STORE_URL = lambda base_url: f"{base_url}/api/v1/store"


def store_command(args: argparse.Namespace) -> int:
    """
    Handle the 'store' command - store items in the vector database.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code
    """
    items = []
    
    if args.file:
        # Load items from file
        try:
            with open(args.file, 'r') as f:
                file_items = json.load(f)
                if isinstance(file_items, list):
                    items.extend(file_items)
                else:
                    items.append(file_items)
        except Exception as e:
            logger.error(f"Error loading items from file: {str(e)}")
            return 1
    
    if args.text:
        # Add text item
        items.append({
            "text": args.text,
            "source": "cli",
            "created_at": None
        })
    
    if args.code:
        # Add code item
        items.append({
            "code": args.code,
            "language": args.language or "unknown",
            "source": "cli",
            "created_at": None
        })
    
    if not items:
        logger.error("No items provided to store. Use --file, --text, or --code.")
        return 1
    
    # Make the request to store items
    try:
        url = STORE_URL(args.base_url)
        response = requests.post(url, json={"items": items})
        
        # Check the response
        if response.status_code == 200:
            logger.info("Items stored successfully!")
            result = response.json()
            logger.info(f"Stored item IDs: {result['ids']}")
            return 0
        else:
            logger.error(f"Error storing items: {response.text}")
            return 1
    except Exception as e:
        logger.error(f"Error making request: {str(e)}")
        return 1


def search_command(args: argparse.Namespace) -> int:
    """
    Handle the 'search' command - search for similar items.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code
    """
    # Prepare the request payload
    payload = {
        "top_k": args.top_k
    }
    
    if args.text:
        payload["text"] = args.text
    elif args.code:
        payload["code"] = args.code
    elif args.table and args.table_file:
        try:
            with open(args.table_file, 'r') as f:
                table_data = json.load(f)
                payload["table"] = table_data
        except Exception as e:
            logger.error(f"Error loading table data from file: {str(e)}")
            return 1
    else:
        logger.error("No search criteria provided. Use --text, --code, or --table.")
        return 1
    
    # Add filter if provided
    if args.filter:
        try:
            filter_data = json.loads(args.filter)
            payload["filter"] = filter_data
        except Exception as e:
            logger.error(f"Error parsing filter JSON: {str(e)}")
            return 1
    
    # Make the request
    try:
        url = SIMILARITY_URL(args.base_url)
        response = requests.post(url, json=payload)
        
        # Check the response
        if response.status_code == 200:
            logger.info("Search successful!")
            results = response.json()
            logger.info(f"Query type: {results['query_type']}")
            logger.info(f"Number of results: {len(results['results'])}")
            
            # Print each result with its similarity score
            for i, result in enumerate(results['results']):
                logger.info(f"\nResult {i+1}, Score: {result['score']:.4f}")
                pprint(result['metadata'])
                logger.info("-----")
            
            # Save results to file if requested
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2)
                logger.info(f"Results saved to {args.output}")
            
            return 0
        else:
            logger.error(f"Error searching: {response.text}")
            return 1
    except Exception as e:
        logger.error(f"Error making request: {str(e)}")
        return 1


def embed_command(args: argparse.Namespace) -> int:
    """
    Handle the 'embed' command - generate embeddings without storing them.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code
    """
    try:
        embedding = None
        
        if args.text:
            logger.info("Generating text embedding...")
            embedding = embed_text(args.text)
        elif args.code:
            logger.info("Generating code embedding...")
            embedding = embed_code(args.code)
        elif args.table and args.table_file:
            logger.info("Generating table embedding...")
            with open(args.table_file, 'r') as f:
                table_data = json.load(f)
            embedding = embed_table(table_data)
        else:
            logger.error("No content provided to embed. Use --text, --code, or --table.")
            return 1
        
        # Convert embedding to list and print
        embedding_list = embedding.tolist()
        
        # Save embedding to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump({"embedding": embedding_list[0]}, f)
            logger.info(f"Embedding saved to {args.output}")
        else:
            # Print first 5 dimensions and shape
            logger.info(f"Embedding shape: {embedding.shape}")
            logger.info(f"First 5 dimensions: {embedding_list[0][:5]}...")
        
        return 0
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        return 1


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Similarity API CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Common arguments
    base_url_arg = lambda p: p.add_argument("--base-url", type=str, default=DEFAULT_BASE_URL, help=f"Base URL of the API. Default: {DEFAULT_BASE_URL}")
    
    # Store command
    store_parser = subparsers.add_parser("store", help="Store items in the vector database")
    base_url_arg(store_parser)
    store_parser.add_argument("--file", type=str, help="JSON file containing items to store")
    store_parser.add_argument("--text", type=str, help="Text content to store")
    store_parser.add_argument("--code", type=str, help="Code content to store")
    store_parser.add_argument("--language", type=str, help="Language of the code (for code storage)")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for similar items")
    base_url_arg(search_parser)
    search_parser.add_argument("--text", type=str, help="Text to search for")
    search_parser.add_argument("--code", type=str, help="Code to search for")
    search_parser.add_argument("--table", action="store_true", help="Search with table data")
    search_parser.add_argument("--table-file", type=str, help="JSON file containing table data for search")
    search_parser.add_argument("--filter", type=str, help="JSON filter criteria for the search")
    search_parser.add_argument("--top-k", type=int, default=5, help="Number of results to return. Default: 5")
    search_parser.add_argument("--output", type=str, help="File to save search results to")
    
    # Embed command
    embed_parser = subparsers.add_parser("embed", help="Generate embeddings without storing them")
    embed_parser.add_argument("--text", type=str, help="Text to embed")
    embed_parser.add_argument("--code", type=str, help="Code to embed")
    embed_parser.add_argument("--table", action="store_true", help="Embed table data")
    embed_parser.add_argument("--table-file", type=str, help="JSON file containing table data for embedding")
    embed_parser.add_argument("--output", type=str, help="File to save embedding to")
    
    args = parser.parse_args()
    
    if args.command == "store":
        return store_command(args)
    elif args.command == "search":
        return search_command(args)
    elif args.command == "embed":
        return embed_command(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())