#!/usr/bin/env python
import argparse
import sys
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Add the parent directory to sys.path to allow importing app
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.graph_ingest.app.db import init_db, get_session
from services.graph_ingest.app.ingestors import GitHubIngestor, CrunchbaseIngestor
from services.graph_ingest.app.models.base import SourceType


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("graph_ingest")


def ingest_github(args: argparse.Namespace) -> Dict[str, Any]:
    """
    Ingest data from GitHub
    
    Args:
        args: Command-line arguments
        
    Returns:
        Dictionary with ingestion results
    """
    # Get the database session
    db = get_session()
    
    # Initialize the GitHub ingestor
    ingestor = GitHubIngestor(db, api_token=args.token)
    
    # Ingest data based on provided arguments
    if args.org:
        result = ingestor.ingest(org=args.org)
    elif args.user:
        result = ingestor.ingest(user=args.user)
    elif args.repo:
        result = ingestor.ingest(repo=args.repo)
    else:
        return {"status": "error", "message": "Must provide one of: --org, --user, or --repo"}
    
    return result


def ingest_crunchbase(args: argparse.Namespace) -> Dict[str, Any]:
    """
    Ingest data from Crunchbase
    
    Args:
        args: Command-line arguments
        
    Returns:
        Dictionary with ingestion results
    """
    # Get the database session
    db = get_session()
    
    # Initialize the Crunchbase ingestor
    ingestor = CrunchbaseIngestor(db, api_key=args.token)
    
    # Ingest data based on provided arguments
    if args.company:
        result = ingestor.ingest(company=args.company)
    elif args.person:
        result = ingestor.ingest(person=args.person)
    else:
        return {"status": "error", "message": "Must provide one of: --company or --person"}
    
    return result


def ingest_command(args: argparse.Namespace) -> int:
    """
    Handle the 'ingest' command
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code
    """
    try:
        # Initialize the database
        init_db()
        
        # Ingest data based on the source
        if args.source.lower() == "github":
            result = ingest_github(args)
        elif args.source.lower() == "crunchbase":
            result = ingest_crunchbase(args)
        else:
            logger.error(f"Unsupported source: {args.source}")
            return 1
        
        # Print the result
        if args.output == "json":
            print(json.dumps(result, indent=2))
        else:
            if result.get("status") == "success":
                print(f"✓ ingest OK")
                if "organization" in result:
                    print(f"  Organization: {result['organization']}")
                    print(f"  Repositories: {result['repositories_count']}")
                elif "user" in result:
                    print(f"  User: {result['user']}")
                    print(f"  Repositories: {result['repositories_count']}")
                elif "repository" in result:
                    print(f"  Repository: {result['repository']}")
                    print(f"  Owner: {result['owner']}")
                    print(f"  Contributors: {result['contributors_count']}")
                elif "company" in result:
                    print(f"  Company: {result['company']}")
                    print(f"  Founders: {result['founders_count']}")
                    print(f"  Funding Rounds: {result['funding_rounds_count']}")
                elif "person" in result:
                    print(f"  Person: {result['person']}")
                    print(f"  Companies Founded: {result['companies_founded_count']}")
            else:
                print(f"✗ ingest FAILED: {result.get('message', 'Unknown error')}")
                return 1
        
        return 0
    except Exception as e:
        logger.exception(f"Error running ingest command: {str(e)}")
        return 1


def server_command(args: argparse.Namespace) -> int:
    """
    Handle the 'server' command
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code
    """
    try:
        # Import here to avoid circular imports
        import uvicorn
        from services.graph_ingest.app.api import create_app
        
        # Initialize the database
        init_db()
        
        # Start the server
        host = args.host or "0.0.0.0"
        port = args.port or 8080
        log_level = args.log_level or "info"
        
        print(f"Starting server on {host}:{port}")
        uvicorn.run(
            "services.graph_ingest.app.api:create_app", 
            factory=True, 
            host=host, 
            port=port, 
            log_level=log_level
        )
        
        return 0
    except Exception as e:
        logger.exception(f"Error running server command: {str(e)}")
        return 1


def main():
    """Main entry point for the CLI"""
    # Create the parser
    parser = argparse.ArgumentParser(
        description="Data Ingestion & Knowledge Graph Service CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest data from a source")
    ingest_parser.add_argument(
        "--source", 
        required=True, 
        choices=["github", "crunchbase"],
        help="Source to ingest data from"
    )
    
    # GitHub-specific arguments
    ingest_parser.add_argument("--org", help="GitHub organization name")
    ingest_parser.add_argument("--user", help="GitHub username")
    ingest_parser.add_argument("--repo", help="GitHub repository in owner/repo format")
    
    # Crunchbase-specific arguments
    ingest_parser.add_argument("--company", help="Crunchbase company permalink")
    ingest_parser.add_argument("--person", help="Crunchbase person permalink")
    
    # Common arguments
    ingest_parser.add_argument(
        "--token", 
        help="API token for the source"
    )
    ingest_parser.add_argument(
        "--output", 
        choices=["text", "json"], 
        default="text",
        help="Output format"
    )
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Run the API server")
    server_parser.add_argument(
        "--host", 
        default="0.0.0.0", 
        help="Host to listen on"
    )
    server_parser.add_argument(
        "--port", 
        type=int, 
        default=8080,
        help="Port to listen on"
    )
    server_parser.add_argument(
        "--log-level", 
        choices=["debug", "info", "warning", "error"], 
        default="info",
        help="Log level"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the appropriate command
    if args.command == "ingest":
        return ingest_command(args)
    elif args.command == "server":
        return server_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())