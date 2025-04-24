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
from services.graph_ingest.app.ingestors import GitHubIngestor, CrunchbaseIngestor, EdgarIngestor, PatentsViewIngestor
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


def ingest_edgar(args: argparse.Namespace) -> Dict[str, Any]:
    """
    Ingest data from SEC EDGAR
    
    Args:
        args: Command-line arguments
        
    Returns:
        Dictionary with ingestion results
    """
    # Get the database session
    db = get_session()
    
    # Initialize the SEC EDGAR ingestor
    ingestor = EdgarIngestor(db, email=args.email)
    
    # Ingest data based on provided arguments
    kwargs = {}
    if args.ticker:
        kwargs["ticker"] = args.ticker
    if args.cik:
        kwargs["cik"] = args.cik
    if args.filing_type:
        kwargs["filing_type"] = args.filing_type
    if args.max_filings:
        kwargs["max_filings"] = args.max_filings
    
    if not (args.ticker or args.cik):
        return {"status": "error", "message": "Must provide either --ticker or --cik"}
    
    result = ingestor.ingest(**kwargs)
    return result


def ingest_patentsview(args: argparse.Namespace) -> Dict[str, Any]:
    """
    Ingest data from PatentsView
    
    Args:
        args: Command-line arguments
        
    Returns:
        Dictionary with ingestion results
    """
    # Get the database session
    db = get_session()
    
    # Initialize the PatentsView ingestor
    ingestor = PatentsViewIngestor(db, api_key=args.token)
    
    # Ingest data based on provided arguments
    kwargs = {}
    if args.company:
        kwargs["company"] = args.company
    if args.assignee:
        kwargs["assignee"] = args.assignee
    if args.max_patents:
        kwargs["max_patents"] = args.max_patents
    
    if not (args.company or args.assignee):
        return {"status": "error", "message": "Must provide either --company or --assignee"}
    
    result = ingestor.ingest(**kwargs)
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
        elif args.source.lower() == "edgar":
            result = ingest_edgar(args)
        elif args.source.lower() == "patentsview":
            result = ingest_patentsview(args)
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
                elif "company" in result and "ticker" in result:
                    # SEC EDGAR result
                    print(f"  Company: {result['company']}")
                    print(f"  Ticker: {result['ticker']}")
                    print(f"  CIK: {result['cik']}")
                    print(f"  Filings: {result['filings_count']}")
                    print(f"  Filing Types: {', '.join(result['filing_types'])}")
                elif "company" in result and "patents_count" in result:
                    # PatentsView result
                    print(f"  Company: {result['company']}")
                    print(f"  Assignee: {result['assignee']}")
                    print(f"  Patents: {result['patents_count']}")
                elif "company" in result:
                    # Crunchbase company result
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
        choices=["github", "crunchbase", "edgar", "patentsview"],
        help="Source to ingest data from"
    )
    
    # GitHub-specific arguments
    ingest_parser.add_argument("--org", help="GitHub organization name")
    ingest_parser.add_argument("--user", help="GitHub username")
    ingest_parser.add_argument("--repo", help="GitHub repository in owner/repo format")
    
    # Crunchbase-specific arguments
    ingest_parser.add_argument("--company", help="Company name (used by Crunchbase and PatentsView)")
    ingest_parser.add_argument("--person", help="Crunchbase person permalink")
    
    # SEC EDGAR-specific arguments
    ingest_parser.add_argument("--ticker", help="Stock ticker symbol (e.g., NVDA, AAPL)")
    ingest_parser.add_argument("--cik", help="SEC CIK number")
    ingest_parser.add_argument("--filing-type", help="Type of filing to look for (default: '10-K,8-K')")
    ingest_parser.add_argument("--max-filings", type=int, help="Maximum number of filings to ingest (default: 10)")
    ingest_parser.add_argument("--email", help="Email for SEC EDGAR User-Agent")
    
    # PatentsView-specific arguments
    ingest_parser.add_argument("--assignee", help="Patent assignee name (usually company name)")
    ingest_parser.add_argument("--max-patents", type=int, help="Maximum number of patents to ingest (default: 20)")
    
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